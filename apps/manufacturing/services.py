"""
Manufacturing business logic services
"""
from decimal import Decimal
from django.db import transaction
from django.utils import timezone

from .models import BillOfMaterials, BOMLine, ManufacturingOrder, ManufacturingOrderLine
from apps.inventory.models import StockMove, Location
from apps.inventory.services import StockService


class BOMService:
    """Service class for BOM operations"""
    
    @staticmethod
    def get_bom_for_product(product):
        """Get active BOM for a product"""
        return BillOfMaterials.objects.filter(
            product=product,
            is_active=True
        ).first()
    
    @staticmethod
    def check_component_availability(bom, quantity, location):
        """
        Check if all components are available for production
        
        Returns:
            dict: {product: {'required': qty, 'available': qty, 'sufficient': bool}}
        """
        result = {}
        
        for line in bom.lines.all():
            required = line.quantity * quantity
            stock = StockService.get_stock_level(line.product, location=location)
            available = stock['available']
            
            result[line.product] = {
                'required': required,
                'available': available,
                'sufficient': available >= required,
                'shortage': max(Decimal('0'), required - available)
            }
        
        return result
    
    @staticmethod
    def calculate_max_production(bom, location):
        """
        Calculate maximum quantity that can be produced based on available stock
        """
        max_qty = None
        
        for line in bom.lines.all():
            if line.quantity <= 0:
                continue
                
            stock = StockService.get_stock_level(line.product, location=location)
            available = stock['available']
            possible = available / line.quantity
            
            if max_qty is None or possible < max_qty:
                max_qty = possible
        
        return max_qty or Decimal('0')


class ManufacturingService:
    """Service class for Manufacturing Order operations"""
    
    @staticmethod
    @transaction.atomic
    def create_mo_from_bom(bom, quantity, source_location, destination_location, user=None, origin=''):
        """
        Create Manufacturing Order from BOM
        """
        mo = ManufacturingOrder.objects.create(
            product=bom.product,
            bom=bom,
            quantity=quantity,
            source_location=source_location,
            destination_location=destination_location,
            origin=origin,
            actor=user
        )
        
        # Create lines from BOM components
        for bom_line in bom.lines.all():
            ManufacturingOrderLine.objects.create(
                manufacturing_order=mo,
                product=bom_line.product,
                quantity_required=bom_line.quantity * quantity,
                uom=bom_line.display_uom,
                actor=user
            )
        
        return mo
    
    @staticmethod
    def confirm_mo(mo):
        """Confirm Manufacturing Order"""
        if mo.state != 'draft':
            raise ValueError("Manufacturing Order must be in draft state to confirm")
        
        mo.state = 'confirmed'
        mo.save(update_fields=['state'])
        return mo
    
    @staticmethod
    def start_production(mo):
        """Start production - change state to in_progress"""
        if mo.state != 'confirmed':
            raise ValueError("Manufacturing Order must be confirmed to start production")
        
        mo.state = 'in_progress'
        mo.date_started = timezone.now()
        mo.save(update_fields=['state', 'date_started'])
        return mo
    
    @staticmethod
    @transaction.atomic
    def consume_components(mo, user=None):
        """
        Consume components from stock
        Creates stock moves for component consumption
        """
        if mo.state != 'in_progress':
            raise ValueError("Manufacturing Order must be in progress to consume components")
        
        # Get production location (where components go during production)
        production_location = Location.objects.filter(
            location_type='production'
        ).first()
        
        if not production_location:
            # Create production location if not exists
            production_location = Location.objects.create(
                name='Production',
                code='PRODUCTION',
                location_type='production',
                actor=user
            )
        
        for line in mo.lines.all():
            if line.quantity_consumed >= line.quantity_required:
                continue  # Already consumed
            
            qty_to_consume = line.quantity_required - line.quantity_consumed
            
            # Create stock move for consumption
            move = StockMove.objects.create(
                product=line.product,
                location_src=mo.source_location,
                location_dest=production_location,
                quantity=qty_to_consume,
                quantity_done=qty_to_consume,
                origin=mo.reference,
                state='done',
                date_done=timezone.now(),
                actor=user
            )
            
            # Update stock
            StockService.update_stock(
                line.product,
                mo.source_location,
                -qty_to_consume
            )
            
            # Update line
            line.quantity_consumed = line.quantity_required
            line.save(update_fields=['quantity_consumed'])
        
        return mo
    
    @staticmethod
    @transaction.atomic
    def produce(mo, quantity_produced, user=None):
        """
        Record production output
        """
        if mo.state != 'in_progress':
            raise ValueError("Manufacturing Order must be in progress to produce")
        
        if quantity_produced <= 0:
            raise ValueError("Quantity must be positive")
        
        if mo.quantity_produced + quantity_produced > mo.quantity:
            raise ValueError("Cannot produce more than ordered quantity")
        
        # Get production location
        production_location = Location.objects.filter(
            location_type='production'
        ).first()
        
        # Create stock move for finished product
        move = StockMove.objects.create(
            product=mo.product,
            location_src=production_location,
            location_dest=mo.destination_location,
            quantity=quantity_produced,
            quantity_done=quantity_produced,
            origin=mo.reference,
            state='done',
            date_done=timezone.now(),
            actor=user
        )
        
        # Update stock for finished product
        # Calculate unit cost based on BOM
        unit_cost = mo.bom.total_cost if mo.bom else mo.product.standard_price
        
        StockService.update_stock(
            mo.product,
            mo.destination_location,
            quantity_produced,
            unit_cost=unit_cost
        )
        
        # Update MO
        mo.quantity_produced += quantity_produced
        mo.save(update_fields=['quantity_produced'])
        
        return mo
    
    @staticmethod
    @transaction.atomic
    def complete_production(mo, user=None):
        """
        Complete the manufacturing order
        - Consume remaining components
        - Produce remaining quantity
        - Mark as done
        """
        if mo.state not in ['confirmed', 'in_progress']:
            raise ValueError("Manufacturing Order must be confirmed or in progress")
        
        # Start if not started
        if mo.state == 'confirmed':
            ManufacturingService.start_production(mo)
        
        # Consume components
        ManufacturingService.consume_components(mo, user)
        
        # Produce remaining quantity
        remaining = mo.quantity - mo.quantity_produced
        if remaining > 0:
            ManufacturingService.produce(mo, remaining, user)
        
        # Mark as done
        mo.state = 'done'
        mo.date_finished = timezone.now()
        mo.save(update_fields=['state', 'date_finished'])
        
        return mo
    
    @staticmethod
    def cancel_mo(mo):
        """Cancel Manufacturing Order"""
        if mo.state == 'done':
            raise ValueError("Cannot cancel completed Manufacturing Order")
        
        if mo.quantity_produced > 0:
            raise ValueError("Cannot cancel Manufacturing Order with produced quantity")
        
        mo.state = 'cancelled'
        mo.save(update_fields=['state'])
        return mo

