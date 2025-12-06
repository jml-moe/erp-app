"""
Stock calculation and business logic services
"""
from decimal import Decimal
from django.db import transaction
from django.db.models import Sum, F
from django.utils import timezone

from .models import StockQuant, StockMove, Location


class StockService:
    """Service class for stock operations"""
    
    @staticmethod
    def get_stock_level(product, location=None, warehouse=None):
        """
        Get current stock level for a product
        
        Args:
            product: Product instance
            location: Optional specific location
            warehouse: Optional warehouse to filter locations
            
        Returns:
            Decimal: Total quantity available
        """
        quants = StockQuant.objects.filter(product=product)
        
        if location:
            quants = quants.filter(location=location)
        elif warehouse:
            quants = quants.filter(location__warehouse=warehouse)
        
        # Only internal locations
        quants = quants.filter(location__location_type='internal')
        
        result = quants.aggregate(
            total=Sum('quantity'),
            reserved=Sum('reserved_quantity')
        )
        
        total = result['total'] or Decimal('0.00')
        reserved = result['reserved'] or Decimal('0.00')
        
        return {
            'quantity': total,
            'reserved': reserved,
            'available': total - reserved
        }
    
    @staticmethod
    def get_all_stock_levels(warehouse=None):
        """
        Get stock levels for all products
        
        Args:
            warehouse: Optional warehouse filter
            
        Returns:
            QuerySet with product stock information
        """
        from apps.products.models import Product
        
        quants = StockQuant.objects.filter(
            location__location_type='internal'
        )
        
        if warehouse:
            quants = quants.filter(location__warehouse=warehouse)
        
        return quants.values(
            'product__id',
            'product__name',
            'product__internal_reference',
            'product__uom__symbol'
        ).annotate(
            total_qty=Sum('quantity'),
            reserved_qty=Sum('reserved_quantity'),
            available_qty=Sum(F('quantity') - F('reserved_quantity'))
        ).order_by('product__name')
    
    @staticmethod
    @transaction.atomic
    def update_stock(product, location, quantity, unit_cost=None):
        """
        Update stock quantity at a location
        
        Args:
            product: Product instance
            location: Location instance
            quantity: Quantity to add (positive) or remove (negative)
            unit_cost: Cost per unit (for incoming stock)
        """
        quant, created = StockQuant.objects.get_or_create(
            product=product,
            location=location,
            defaults={
                'quantity': Decimal('0.00'),
                'unit_cost': unit_cost or product.standard_price
            }
        )
        
        quant.quantity += quantity
        
        if unit_cost and quantity > 0:
            # Update average cost
            if quant.quantity > 0:
                old_value = (quant.quantity - quantity) * quant.unit_cost
                new_value = quantity * unit_cost
                quant.unit_cost = (old_value + new_value) / quant.quantity
        
        quant.save()
        return quant
    
    @staticmethod
    @transaction.atomic
    def reserve_stock(product, location, quantity):
        """
        Reserve stock for a pending move
        
        Args:
            product: Product instance
            location: Source location
            quantity: Quantity to reserve
            
        Returns:
            bool: True if reservation successful
        """
        quants = StockQuant.objects.filter(
            product=product,
            location=location
        ).select_for_update()
        
        available = sum(q.available_quantity for q in quants)
        
        if available < quantity:
            return False
        
        remaining = quantity
        for quant in quants:
            if remaining <= 0:
                break
            
            reserve = min(quant.available_quantity, remaining)
            quant.reserved_quantity += reserve
            quant.save()
            remaining -= reserve
        
        return True
    
    @staticmethod
    @transaction.atomic
    def unreserve_stock(product, location, quantity):
        """
        Release reserved stock
        """
        quants = StockQuant.objects.filter(
            product=product,
            location=location,
            reserved_quantity__gt=0
        ).select_for_update()
        
        remaining = quantity
        for quant in quants:
            if remaining <= 0:
                break
            
            release = min(quant.reserved_quantity, remaining)
            quant.reserved_quantity -= release
            quant.save()
            remaining -= release
    
    @staticmethod
    @transaction.atomic
    def process_move(move):
        """
        Process a stock move - update source and destination quants
        
        Args:
            move: StockMove instance
        """
        if move.state == 'done':
            raise ValueError("Move already processed")
        
        # Remove from source
        StockService.update_stock(
            move.product,
            move.location_src,
            -move.quantity_done
        )
        
        # Add to destination
        StockService.update_stock(
            move.product,
            move.location_dest,
            move.quantity_done,
            unit_cost=move.unit_price
        )
        
        # Update move
        move.state = 'done'
        move.date_done = timezone.now()
        move.save()
    
    @staticmethod
    def get_low_stock_products(warehouse=None):
        """
        Get products below reorder point
        """
        from apps.products.models import Product
        
        products = Product.objects.filter(
            is_active=True,
            product_type='stockable',
            reorder_point__gt=0
        )
        
        low_stock = []
        for product in products:
            stock = StockService.get_stock_level(product, warehouse=warehouse)
            if stock['available'] <= product.reorder_point:
                low_stock.append({
                    'product': product,
                    'available': stock['available'],
                    'reorder_point': product.reorder_point,
                    'reorder_qty': product.reorder_qty
                })
        
        return low_stock
    
    @staticmethod
    def get_stock_valuation(warehouse=None):
        """
        Get total stock valuation
        """
        quants = StockQuant.objects.filter(
            location__location_type='internal',
            quantity__gt=0
        )
        
        if warehouse:
            quants = quants.filter(location__warehouse=warehouse)
        
        return quants.aggregate(
            total_value=Sum(F('quantity') * F('unit_cost'))
        )['total_value'] or Decimal('0.00')

