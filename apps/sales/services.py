from decimal import Decimal
from django.utils import timezone
from django.db import transaction

from .models import (
    SalesQuotation, SalesQuotationLine,
    SalesOrder, SalesOrderLine,
    SalesInvoice, SalesInvoiceLine
)
from apps.inventory.models import StockPicking, StockPickingLine, Location
from apps.inventory.services import StockService


class SalesService:
    """Service for handling sales operations"""
    
    @staticmethod
    @transaction.atomic
    def convert_quotation_to_order(quotation: SalesQuotation, source_location=None) -> SalesOrder:
        """Convert a confirmed quotation to a sales order"""
        if quotation.state != 'sent':
            raise ValueError("Only sent quotations can be converted to orders")

        # Create Sales Order
        sales_order = SalesOrder.objects.create(
            customer=quotation.customer,
            quotation=quotation,
            discount_amount=quotation.discount_amount,
            source_location=source_location,
            notes=quotation.notes,
        )

        # Copy lines
        for sq_line in quotation.lines.all():
            SalesOrderLine.objects.create(
                sales_order=sales_order,
                product=sq_line.product,
                description=sq_line.description,
                quantity=sq_line.quantity,
                unit_price=sq_line.unit_price,
                discount_percent=sq_line.discount_percent,
            )

        # Update quotation
        quotation.state = 'confirmed'
        quotation.sales_order = sales_order
        quotation.save()

        return sales_order
    
    @staticmethod
    @transaction.atomic
    def confirm_order(sales_order: SalesOrder):
        """Confirm a sales order and reserve stock"""
        if sales_order.state != 'draft':
            raise ValueError("Only draft orders can be confirmed")

        if not sales_order.source_location:
            raise ValueError("Sales order must have a source location for stock reservation")

        # Reserve stock for each line
        for line in sales_order.lines.all():
            success = StockService.reserve_stock(
                line.product,
                sales_order.source_location,
                line.quantity
            )
            if not success:
                raise ValueError(f"Insufficient stock for {line.product.name}. Available: {StockService.get_stock_level(line.product, sales_order.source_location)['available']}")

        sales_order.state = 'confirmed'
        sales_order.save()
    
    @staticmethod
    @transaction.atomic
    def mark_order_processing(sales_order: SalesOrder, user=None):
        """Mark order as processing (being prepared) and create delivery picking"""
        if sales_order.state != 'confirmed':
            raise ValueError("Only confirmed orders can be marked as processing")

        if sales_order.picking:
            raise ValueError("Order already has a delivery picking")

        # Get customer location (or create one)
        customer_location = Location.objects.filter(
            location_type='customer'
        ).first()

        if not customer_location:
            customer_location = Location.objects.create(
                name='Customer Deliveries',
                code='CUST',
                location_type='customer',
                actor=user
            )

        # Create delivery picking
        picking = StockPicking.objects.create(
            picking_type='outgoing',
            location_src=sales_order.source_location,
            location_dest=customer_location,
            origin=sales_order.reference,
            scheduled_date=sales_order.expected_date,
            actor=user
        )

        # Create picking lines from SO lines
        for so_line in sales_order.lines.all():
            remaining = so_line.quantity - so_line.quantity_delivered
            if remaining > 0:
                StockPickingLine.objects.create(
                    picking=picking,
                    product=so_line.product,
                    quantity=remaining,
                    actor=user
                )

        sales_order.picking = picking
        sales_order.state = 'processing'
        sales_order.save()

        return picking
    
    @staticmethod
    @transaction.atomic
    def mark_order_ready(sales_order: SalesOrder):
        """Mark order as ready for pickup/delivery"""
        if sales_order.state != 'processing':
            raise ValueError("Only processing orders can be marked as ready")
        
        sales_order.state = 'ready'
        sales_order.save()
    
    @staticmethod
    @transaction.atomic
    def deliver_order(sales_order: SalesOrder, delivered_quantities=None, user=None):
        """Mark order as delivered and process stock movements"""
        from apps.inventory.models import StockMove
        from django.utils import timezone

        if sales_order.state not in ['ready', 'confirmed', 'processing']:
            raise ValueError("Order cannot be delivered in current state")

        if not sales_order.picking:
            raise ValueError("Order must have a delivery picking to be delivered")

        # Get customer location
        customer_location = sales_order.picking.location_dest

        # Process delivery - create stock moves for delivered quantities
        if delivered_quantities:
            for line_id, qty in delivered_quantities.items():
                so_line = sales_order.lines.get(id=line_id)

                if qty <= 0:
                    continue

                # Create stock move for delivery
                move = StockMove.objects.create(
                    product=so_line.product,
                    location_src=sales_order.source_location,
                    location_dest=customer_location,
                    quantity=qty,
                    quantity_done=qty,
                    unit_price=so_line.unit_price,
                    origin=sales_order.reference,
                    state='done',
                    date_done=timezone.now(),
                    actor=user
                )

                # Update stock (remove from inventory)
                StockService.update_stock(
                    so_line.product,
                    sales_order.source_location,
                    -qty
                )

                # Update SO line
                so_line.quantity_delivered += qty
                so_line.save(update_fields=['quantity_delivered'])

                # Release reserved stock for delivered quantity
                StockService.unreserve_stock(
                    so_line.product,
                    sales_order.source_location,
                    qty
                )
        else:
            # Deliver all remaining quantities
            for line in sales_order.lines.all():
                qty_to_deliver = line.quantity - line.quantity_delivered
                if qty_to_deliver > 0:
                    # Create stock move for delivery
                    move = StockMove.objects.create(
                        product=line.product,
                        location_src=sales_order.source_location,
                        location_dest=customer_location,
                        quantity=qty_to_deliver,
                        quantity_done=qty_to_deliver,
                        unit_price=line.unit_price,
                        origin=sales_order.reference,
                        state='done',
                        date_done=timezone.now(),
                        actor=user
                    )

                    # Update stock (remove from inventory)
                    StockService.update_stock(
                        line.product,
                        sales_order.source_location,
                        -qty_to_deliver
                    )

                    # Update SO line
                    line.quantity_delivered = line.quantity
                    line.save(update_fields=['quantity_delivered'])

                    # Release all reserved stock for this line
                    StockService.unreserve_stock(
                        line.product,
                        sales_order.source_location,
                        qty_to_deliver
                    )

        # Check if all lines are fully delivered
        fully_delivered = all(
            line.quantity_delivered >= line.quantity
            for line in sales_order.lines.all()
        )

        if fully_delivered:
            sales_order.state = 'delivered'
        else:
            sales_order.state = 'delivered'  # Still mark as delivered even if partial

        sales_order.save()

        return sales_order
    
    @staticmethod
    @transaction.atomic
    def complete_order(sales_order: SalesOrder):
        """Mark order as done (completed)"""
        if sales_order.state != 'delivered':
            raise ValueError("Only delivered orders can be marked as done")
        
        sales_order.state = 'done'
        sales_order.save()
    
    @staticmethod
    @transaction.atomic
    def cancel_order(sales_order: SalesOrder):
        """Cancel a sales order"""
        if sales_order.state in ['done', 'cancelled']:
            raise ValueError("Order cannot be cancelled in current state")
        
        sales_order.state = 'cancelled'
        sales_order.save()
    
    @staticmethod
    @transaction.atomic
    def create_invoice_from_order(sales_order: SalesOrder) -> SalesInvoice:
        """Create an invoice from a sales order"""
        if sales_order.state not in ['delivered', 'done']:
            raise ValueError("Order must be delivered before invoicing")
        
        # Check if already fully invoiced
        existing_invoices = sales_order.invoices.exclude(state='cancelled')
        total_invoiced = sum(inv.total_amount for inv in existing_invoices)
        if total_invoiced >= sales_order.total_amount:
            raise ValueError("Order is already fully invoiced")
        
        # Create Invoice
        invoice = SalesInvoice.objects.create(
            customer=sales_order.customer,
            sales_order=sales_order,
            discount_amount=sales_order.discount_amount,
            due_date=timezone.now().date(),  # Due immediately for cafe
        )
        
        # Copy lines from order
        for so_line in sales_order.lines.all():
            qty_to_invoice = so_line.quantity - so_line.quantity_invoiced
            if qty_to_invoice > 0:
                SalesInvoiceLine.objects.create(
                    invoice=invoice,
                    product=so_line.product,
                    description=so_line.description,
                    quantity=qty_to_invoice,
                    unit_price=so_line.unit_price,
                    discount_percent=so_line.discount_percent,
                )
                # Update invoiced quantity on SO line
                so_line.quantity_invoiced = so_line.quantity
                so_line.save(update_fields=['quantity_invoiced'])
        
        return invoice
    
    @staticmethod
    @transaction.atomic
    def record_payment(
        invoice: SalesInvoice, 
        amount: Decimal,
        payment_method: str,
        payment_reference: str = ''
    ):
        """Record a payment on an invoice"""
        if invoice.state in ['paid', 'cancelled']:
            raise ValueError("Invoice cannot accept payments in current state")
        
        invoice.amount_paid += amount
        invoice.payment_method = payment_method
        invoice.payment_reference = payment_reference
        invoice.payment_date = timezone.now().date()
        
        # Update state based on payment
        if invoice.amount_paid >= invoice.total_amount:
            invoice.state = 'paid'
            invoice.amount_due = Decimal('0.00')
        else:
            invoice.state = 'partial'
            invoice.amount_due = invoice.total_amount - invoice.amount_paid
        
        invoice.save()
    
    @staticmethod
    @transaction.atomic
    def cancel_invoice(invoice: SalesInvoice):
        """Cancel an invoice"""
        if invoice.state == 'paid':
            raise ValueError("Paid invoices cannot be cancelled")
        
        invoice.state = 'cancelled'
        invoice.save()

