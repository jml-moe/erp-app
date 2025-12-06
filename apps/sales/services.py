from decimal import Decimal
from django.utils import timezone
from django.db import transaction

from .models import (
    SalesQuotation, SalesQuotationLine,
    SalesOrder, SalesOrderLine,
    SalesInvoice, SalesInvoiceLine
)


class SalesService:
    """Service for handling sales operations"""
    
    @staticmethod
    @transaction.atomic
    def convert_quotation_to_order(quotation: SalesQuotation) -> SalesOrder:
        """Convert a confirmed quotation to a sales order"""
        if quotation.state != 'sent':
            raise ValueError("Only sent quotations can be converted to orders")
        
        # Create Sales Order
        sales_order = SalesOrder.objects.create(
            customer=quotation.customer,
            discount_amount=quotation.discount_amount,
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
        """Confirm a sales order"""
        if sales_order.state != 'draft':
            raise ValueError("Only draft orders can be confirmed")
        
        sales_order.state = 'confirmed'
        sales_order.save()
    
    @staticmethod
    @transaction.atomic
    def mark_order_processing(sales_order: SalesOrder):
        """Mark order as processing (being prepared)"""
        if sales_order.state != 'confirmed':
            raise ValueError("Only confirmed orders can be marked as processing")
        
        sales_order.state = 'processing'
        sales_order.save()
    
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
    def deliver_order(sales_order: SalesOrder):
        """Mark order as delivered"""
        if sales_order.state not in ['ready', 'confirmed', 'processing']:
            raise ValueError("Order cannot be delivered in current state")
        
        # Mark all lines as delivered
        for line in sales_order.lines.all():
            line.quantity_delivered = line.quantity
            line.save(update_fields=['quantity_delivered'])
        
        sales_order.state = 'delivered'
        sales_order.save()
    
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

