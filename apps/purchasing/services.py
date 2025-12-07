"""
Purchasing business logic services
"""
from decimal import Decimal
from django.db import transaction
from django.utils import timezone

from .models import RequestForQuotation, RFQLine, PurchaseOrder, POLine
from apps.inventory.models import Location, StockPicking, StockPickingLine
from apps.inventory.services import StockService


class RFQService:
    """Service class for RFQ operations"""
    
    @staticmethod
    def send_rfq(rfq):
        """Mark RFQ as sent to vendor"""
        if rfq.state != 'draft':
            raise ValueError("RFQ must be in draft state to send")
        
        rfq.state = 'sent'
        rfq.save(update_fields=['state'])
        return rfq
    
    @staticmethod
    def receive_quotation(rfq):
        """Mark that quotation has been received from vendor"""
        if rfq.state != 'sent':
            raise ValueError("RFQ must be in sent state")
        
        rfq.state = 'received'
        rfq.save(update_fields=['state'])
        return rfq
    
    @staticmethod
    @transaction.atomic
    def convert_to_po(rfq, delivery_location=None, user=None):
        """Convert RFQ to Purchase Order"""
        if rfq.state not in ['received', 'sent']:
            raise ValueError("RFQ must be in sent or received state to convert")
        
        if rfq.purchase_order:
            raise ValueError("RFQ already has a Purchase Order")
        
        # Create PO
        po = PurchaseOrder.objects.create(
            vendor=rfq.vendor,
            delivery_location=delivery_location,
            expected_date=rfq.deadline,
            notes=rfq.notes,
            actor=user
        )
        
        # Copy lines
        for rfq_line in rfq.lines.all():
            POLine.objects.create(
                purchase_order=po,
                product=rfq_line.product,
                description=rfq_line.description,
                quantity=rfq_line.quantity,
                unit_price=rfq_line.unit_price,
                actor=user
            )
        
        # Link and update states
        rfq.purchase_order = po
        rfq.state = 'done'
        rfq.save(update_fields=['purchase_order', 'state'])
        
        return po
    
    @staticmethod
    def cancel_rfq(rfq):
        """Cancel RFQ"""
        if rfq.state == 'done':
            raise ValueError("Cannot cancel RFQ that has been converted to PO")
        
        rfq.state = 'cancelled'
        rfq.save(update_fields=['state'])
        return rfq


class POService:
    """Service class for Purchase Order operations"""
    
    @staticmethod
    def confirm_po(po):
        """Confirm Purchase Order"""
        if po.state != 'draft':
            raise ValueError("PO must be in draft state to confirm")
        
        po.state = 'confirmed'
        po.save(update_fields=['state'])
        return po
    
    @staticmethod
    def send_po(po):
        """Mark PO as sent to vendor"""
        if po.state != 'confirmed':
            raise ValueError("PO must be confirmed to send")
        
        po.state = 'sent'
        po.save(update_fields=['state'])
        return po
    
    @staticmethod
    @transaction.atomic
    def create_receipt(po, user=None):
        """Create stock picking for receiving PO"""
        if po.state not in ['sent', 'partially_received']:
            raise ValueError("PO must be sent or partially received to create receipt")
        
        if not po.delivery_location:
            raise ValueError("PO must have a delivery location")
        
        # Get supplier location (or create one)
        supplier_location = Location.objects.filter(
            location_type='supplier'
        ).first()
        
        if not supplier_location:
            supplier_location = Location.objects.create(
                name='Suppliers',
                code='SUPPLIERS',
                location_type='supplier',
                actor=user
            )
        
        # Create picking
        picking = StockPicking.objects.create(
            picking_type='incoming',
            location_src=supplier_location,
            location_dest=po.delivery_location,
            origin=po.reference,
            scheduled_date=po.expected_date,
            actor=user
        )
        
        # Create picking lines from PO lines that haven't been fully received
        for po_line in po.lines.filter(quantity_received__lt=models.F('quantity')):
            remaining = po_line.quantity - po_line.quantity_received
            if remaining > 0:
                StockPickingLine.objects.create(
                    picking=picking,
                    product=po_line.product,
                    quantity=remaining,
                    actor=user
                )
        
        po.picking = picking
        po.save(update_fields=['picking'])
        
        return picking
    
    @staticmethod
    @transaction.atomic
    def receive_products(po, received_quantities, user=None):
        """
        Receive products for PO
        
        Args:
            po: PurchaseOrder instance
            received_quantities: dict of {po_line_id: quantity_received}
            user: User performing the action
        """
        from apps.inventory.models import StockMove
        
        if po.state not in ['sent', 'partially_received']:
            raise ValueError("PO must be sent or partially received")
        
        if not po.delivery_location:
            raise ValueError("PO must have a delivery location")
        
        # Get supplier location
        supplier_location = Location.objects.filter(
            location_type='supplier'
        ).first()
        
        fully_received = True
        
        for line_id, qty in received_quantities.items():
            po_line = po.lines.get(id=line_id)
            
            if qty <= 0:
                continue
            
            # Create stock move
            move = StockMove.objects.create(
                product=po_line.product,
                location_src=supplier_location,
                location_dest=po.delivery_location,
                quantity=qty,
                quantity_done=qty,
                unit_price=po_line.unit_price,
                origin=po.reference,
                state='done',
                date_done=timezone.now(),
                actor=user
            )
            
            # Update stock
            StockService.update_stock(
                po_line.product,
                po.delivery_location,
                qty,
                unit_cost=po_line.unit_price
            )
            
            # Update PO line
            po_line.quantity_received += qty
            po_line.save(update_fields=['quantity_received'])
            
            if po_line.quantity_received < po_line.quantity:
                fully_received = False
        
        # Check if all lines are fully received
        for line in po.lines.all():
            if line.quantity_received < line.quantity:
                fully_received = False
                break
        
        if fully_received:
            po.state = 'received'
        else:
            po.state = 'partially_received'
        
        po.save(update_fields=['state'])
        
        return po
    
    @staticmethod
    def mark_billed(po):
        """Mark PO as billed"""
        if po.state != 'received':
            raise ValueError("PO must be fully received before billing")
        
        po.state = 'billed'
        po.save(update_fields=['state'])
        return po
    
    @staticmethod
    def mark_done(po):
        """Mark PO as done"""
        if po.state != 'billed':
            raise ValueError("PO must be billed before marking as done")
        
        po.state = 'done'
        po.save(update_fields=['state'])
        return po
    
    @staticmethod
    def mark_billed(po, bill_reference='', bill_date=None, bill_amount=None):
        """Mark PO as billed by vendor"""
        if po.state != 'received':
            raise ValueError("PO must be fully received before billing")

        po.state = 'billed'
        if bill_reference:
            po.bill_reference = bill_reference
        if bill_date:
            po.bill_date = bill_date
        if bill_amount is not None:
            po.bill_amount = bill_amount
        else:
            po.bill_amount = po.total_amount
        po.save(update_fields=['state', 'bill_reference', 'bill_date', 'bill_amount'])
        return po

    @staticmethod
    def record_payment(po, payment_date=None, payment_reference=''):
        """Record payment made to vendor"""
        if po.state != 'billed':
            raise ValueError("PO must be billed before recording payment")

        po.state = 'done'
        po.payment_date = payment_date or timezone.now().date()
        po.payment_reference = payment_reference
        po.save(update_fields=['state', 'payment_date', 'payment_reference'])
        return po

    @staticmethod
    def cancel_po(po):
        """Cancel Purchase Order"""
        if po.state in ['received', 'billed', 'done']:
            raise ValueError("Cannot cancel PO that has been received or billed")

        po.state = 'cancelled'
        po.save(update_fields=['state'])
        return po


# Import models for F expression
from django.db import models

