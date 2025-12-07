from django.db import models
from decimal import Decimal
from django.utils import timezone

from core.models import BaseModel
from apps.products.models import Product
from apps.vendors.models import Vendor
from apps.inventory.models import Location, StockPicking


# RFQ States
RFQ_STATE_CHOICES = (
    ('draft', 'Draft'),
    ('sent', 'Sent to Vendor'),
    ('received', 'Quotation Received'),
    ('cancelled', 'Cancelled'),
    ('done', 'Done'),  # Converted to PO
)

# PO States
PO_STATE_CHOICES = (
    ('draft', 'Draft'),
    ('confirmed', 'Confirmed'),
    ('sent', 'Sent to Vendor'),
    ('partially_received', 'Partially Received'),
    ('received', 'Received'),
    ('billed', 'Billed'),
    ('done', 'Done'),
    ('cancelled', 'Cancelled'),
)


class RequestForQuotation(BaseModel):
    """Request for Quotation to vendors"""
    reference = models.CharField(max_length=50, unique=True, blank=True)
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name='rfqs'
    )
    
    # Dates
    date = models.DateField(auto_now_add=True)
    deadline = models.DateField(null=True, blank=True, help_text='Response deadline')
    
    # State
    state = models.CharField(
        max_length=20,
        choices=RFQ_STATE_CHOICES,
        default='draft'
    )
    
    # Totals
    untaxed_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00')
    )
    tax_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00')
    )
    total_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    notes = models.TextField(blank=True)
    
    # Link to PO if converted
    purchase_order = models.OneToOneField(
        'PurchaseOrder',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rfq_source'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Request for Quotation'
        verbose_name_plural = 'Requests for Quotation'

    def __str__(self):
        return f"{self.reference} - {self.vendor.name}"

    def save(self, *args, **kwargs):
        if not self.reference:
            last_rfq = RequestForQuotation.objects.filter(
                reference__startswith='RFQ-'
            ).order_by('-reference').first()
            
            if last_rfq and last_rfq.reference:
                try:
                    last_num = int(last_rfq.reference.split('-')[1])
                    self.reference = f'RFQ-{last_num + 1:05d}'
                except (ValueError, IndexError):
                    self.reference = 'RFQ-00001'
            else:
                self.reference = 'RFQ-00001'
        
        super().save(*args, **kwargs)

    def compute_totals(self):
        """Compute total amounts from lines"""
        lines = self.lines.all()
        self.untaxed_amount = sum(line.subtotal for line in lines)
        self.tax_amount = self.untaxed_amount * Decimal('0.11')  # PPN 11%
        self.total_amount = self.untaxed_amount + self.tax_amount
        self.save(update_fields=['untaxed_amount', 'tax_amount', 'total_amount'])


class RFQLine(BaseModel):
    """Line item in RFQ"""
    rfq = models.ForeignKey(
        RequestForQuotation,
        on_delete=models.CASCADE,
        related_name='lines'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='rfq_lines'
    )
    description = models.CharField(max_length=255, blank=True)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Pricing (filled when quotation received)
    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    subtotal = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00')
    )

    class Meta:
        ordering = ['rfq', 'id']

    def __str__(self):
        return f"{self.rfq.reference}: {self.product.name} x {self.quantity}"

    def save(self, *args, **kwargs):
        if not self.description:
            self.description = self.product.name
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        # Update RFQ totals
        self.rfq.compute_totals()


class PurchaseOrder(BaseModel):
    """Purchase Order"""
    reference = models.CharField(max_length=50, unique=True, blank=True)
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name='purchase_orders'
    )
    
    # Dates
    date = models.DateField(auto_now_add=True)
    expected_date = models.DateField(null=True, blank=True)
    
    # State
    state = models.CharField(
        max_length=20,
        choices=PO_STATE_CHOICES,
        default='draft'
    )
    
    # Delivery
    delivery_location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        related_name='purchase_orders'
    )
    
    # Totals
    untaxed_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00')
    )
    tax_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00')
    )
    total_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    notes = models.TextField(blank=True)
    
    # Related picking for receiving
    picking = models.ForeignKey(
        StockPicking,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='purchase_orders'
    )

    # Vendor billing
    bill_reference = models.CharField(max_length=50, blank=True, help_text='Vendor bill/invoice reference')
    bill_date = models.DateField(null=True, blank=True, help_text='Date of vendor bill')
    bill_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Amount billed by vendor'
    )
    payment_date = models.DateField(null=True, blank=True, help_text='Date payment was made')
    payment_reference = models.CharField(max_length=100, blank=True, help_text='Payment reference')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reference} - {self.vendor.name}"

    def save(self, *args, **kwargs):
        if not self.reference:
            last_po = PurchaseOrder.objects.filter(
                reference__startswith='PO-'
            ).order_by('-reference').first()
            
            if last_po and last_po.reference:
                try:
                    last_num = int(last_po.reference.split('-')[1])
                    self.reference = f'PO-{last_num + 1:05d}'
                except (ValueError, IndexError):
                    self.reference = 'PO-00001'
            else:
                self.reference = 'PO-00001'
        
        super().save(*args, **kwargs)

    def compute_totals(self):
        """Compute total amounts from lines"""
        lines = self.lines.all()
        self.untaxed_amount = sum(line.subtotal for line in lines)
        self.tax_amount = self.untaxed_amount * Decimal('0.11')  # PPN 11%
        self.total_amount = self.untaxed_amount + self.tax_amount
        self.save(update_fields=['untaxed_amount', 'tax_amount', 'total_amount'])

    @property
    def received_percentage(self):
        """Calculate percentage of items received"""
        lines = self.lines.all()
        if not lines:
            return 0
        total_qty = sum(line.quantity for line in lines)
        received_qty = sum(line.quantity_received for line in lines)
        if total_qty == 0:
            return 0
        return (received_qty / total_qty) * 100


class POLine(BaseModel):
    """Line item in Purchase Order"""
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name='lines'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='po_lines'
    )
    description = models.CharField(max_length=255, blank=True)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    quantity_received = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    quantity_billed = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Pricing
    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    subtotal = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00')
    )

    class Meta:
        ordering = ['purchase_order', 'id']

    def __str__(self):
        return f"{self.purchase_order.reference}: {self.product.name} x {self.quantity}"

    def save(self, *args, **kwargs):
        if not self.description:
            self.description = self.product.name
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        # Update PO totals
        self.purchase_order.compute_totals()

    @property
    def is_fully_received(self):
        return self.quantity_received >= self.quantity

    @property
    def remaining_qty(self):
        return self.quantity - self.quantity_received

