from django.db import models
from decimal import Decimal
from django.utils import timezone

from core.models import BaseModel
from apps.products.models import Product
from apps.inventory.models import Location, StockPicking


# Customer Types
CUSTOMER_TYPE_CHOICES = (
    ('individual', 'Individual'),
    ('company', 'Company'),
)

# Quotation States
QUOTATION_STATE_CHOICES = (
    ('draft', 'Draft'),
    ('sent', 'Sent'),
    ('confirmed', 'Confirmed'),  # Converted to SO
    ('cancelled', 'Cancelled'),
    ('expired', 'Expired'),
)

# Sales Order States
SO_STATE_CHOICES = (
    ('draft', 'Draft'),
    ('confirmed', 'Confirmed'),
    ('processing', 'Processing'),
    ('ready', 'Ready'),
    ('delivered', 'Delivered'),
    ('done', 'Done'),
    ('cancelled', 'Cancelled'),
)

# Invoice States
INVOICE_STATE_CHOICES = (
    ('draft', 'Draft'),
    ('sent', 'Sent'),
    ('paid', 'Paid'),
    ('partial', 'Partially Paid'),
    ('overdue', 'Overdue'),
    ('cancelled', 'Cancelled'),
)

# Payment Methods
PAYMENT_METHOD_CHOICES = (
    ('cash', 'Cash'),
    ('bank_transfer', 'Bank Transfer'),
    ('credit_card', 'Credit Card'),
    ('debit_card', 'Debit Card'),
    ('e_wallet', 'E-Wallet'),
    ('qris', 'QRIS'),
)


class Customer(BaseModel):
    """Customer/Client for sales"""
    name = models.CharField(max_length=255)
    customer_type = models.CharField(
        max_length=20,
        choices=CUSTOMER_TYPE_CHOICES,
        default='individual'
    )
    
    # Contact Information
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    mobile = models.CharField(max_length=20, blank=True)
    
    # Address
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    
    # Business Info (for company type)
    company_name = models.CharField(max_length=255, blank=True)
    tax_id = models.CharField(max_length=50, blank=True, help_text='NPWP')
    
    # Loyalty
    loyalty_points = models.IntegerField(default=0)
    
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        if self.customer_type == 'company' and self.company_name:
            return f"{self.company_name} ({self.name})"
        return self.name

    @property
    def total_orders(self):
        return self.sales_orders.count()

    @property
    def total_spent(self):
        return self.sales_orders.filter(
            state='done'
        ).aggregate(
            total=models.Sum('total_amount')
        )['total'] or Decimal('0.00')


class SalesQuotation(BaseModel):
    """Sales Quotation before converting to Sales Order"""
    reference = models.CharField(max_length=50, unique=True, blank=True)
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='quotations'
    )

    # Dates
    date = models.DateField(auto_now_add=True)
    validity_date = models.DateField(
        null=True,
        blank=True,
        help_text='Quotation valid until this date'
    )

    # State
    state = models.CharField(
        max_length=20,
        choices=QUOTATION_STATE_CHOICES,
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
    discount_amount = models.DecimalField(
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

    # Link to SO if converted
    sales_order = models.OneToOneField(
        'SalesOrder',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quotation_source'
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reference} - {self.customer.name}"

    def save(self, *args, **kwargs):
        if not self.reference:
            last_sq = SalesQuotation.objects.filter(
                reference__startswith='SQ-'
            ).order_by('-reference').first()
            
            if last_sq and last_sq.reference:
                try:
                    last_num = int(last_sq.reference.split('-')[1])
                    self.reference = f'SQ-{last_num + 1:05d}'
                except (ValueError, IndexError):
                    self.reference = 'SQ-00001'
            else:
                self.reference = 'SQ-00001'
        
        super().save(*args, **kwargs)

    def compute_totals(self):
        """Compute total amounts from lines"""
        lines = self.lines.all()
        self.untaxed_amount = sum(line.subtotal for line in lines)
        self.tax_amount = self.untaxed_amount * Decimal('0.11')  # PPN 11%
        self.total_amount = self.untaxed_amount + self.tax_amount - self.discount_amount
        self.save(update_fields=['untaxed_amount', 'tax_amount', 'total_amount'])

    @property
    def is_expired(self):
        if self.validity_date and self.state == 'sent':
            return timezone.now().date() > self.validity_date
        return False


class SalesQuotationLine(BaseModel):
    """Line item in Sales Quotation"""
    quotation = models.ForeignKey(
        SalesQuotation,
        on_delete=models.CASCADE,
        related_name='lines'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='quotation_lines'
    )
    description = models.CharField(max_length=255, blank=True)
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=1)
    
    # Pricing
    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00')
    )
    subtotal = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00')
    )

    class Meta:
        ordering = ['quotation', 'id']

    def __str__(self):
        return f"{self.quotation.reference}: {self.product.name} x {self.quantity}"

    def save(self, *args, **kwargs):
        if not self.description:
            self.description = self.product.name
        if self.unit_price == 0 and self.product.list_price:
            self.unit_price = self.product.list_price
        
        # Calculate subtotal with discount
        base_amount = self.quantity * self.unit_price
        discount = base_amount * (self.discount_percent / 100)
        self.subtotal = base_amount - discount
        
        super().save(*args, **kwargs)
        self.quotation.compute_totals()


class SalesOrder(BaseModel):
    """Sales Order"""
    reference = models.CharField(max_length=50, unique=True, blank=True)
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='sales_orders'
    )

    # Link to quotation source
    quotation = models.OneToOneField(
        'SalesQuotation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='converted_order'
    )

    # Dates
    date = models.DateField(auto_now_add=True)
    expected_date = models.DateField(
        null=True,
        blank=True,
        help_text='Expected delivery/pickup date'
    )

    # State
    state = models.CharField(
        max_length=20,
        choices=SO_STATE_CHOICES,
        default='draft'
    )

    # Location (for internal stock operations)
    source_location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sales_orders'
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
    discount_amount = models.DecimalField(
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

    # Related picking for delivery
    picking = models.ForeignKey(
        StockPicking,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sales_orders'
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reference} - {self.customer.name}"

    def save(self, *args, **kwargs):
        if not self.reference:
            last_so = SalesOrder.objects.filter(
                reference__startswith='SO-'
            ).order_by('-reference').first()
            
            if last_so and last_so.reference:
                try:
                    last_num = int(last_so.reference.split('-')[1])
                    self.reference = f'SO-{last_num + 1:05d}'
                except (ValueError, IndexError):
                    self.reference = 'SO-00001'
            else:
                self.reference = 'SO-00001'
        
        super().save(*args, **kwargs)

    def compute_totals(self):
        """Compute total amounts from lines"""
        lines = self.lines.all()
        self.untaxed_amount = sum(line.subtotal for line in lines)
        self.tax_amount = self.untaxed_amount * Decimal('0.11')  # PPN 11%
        self.total_amount = self.untaxed_amount + self.tax_amount - self.discount_amount
        self.save(update_fields=['untaxed_amount', 'tax_amount', 'total_amount'])

    @property
    def delivered_percentage(self):
        """Calculate percentage of items delivered"""
        lines = self.lines.all()
        if not lines:
            return 0
        total_qty = sum(line.quantity for line in lines)
        delivered_qty = sum(line.quantity_delivered for line in lines)
        if total_qty == 0:
            return 0
        return (delivered_qty / total_qty) * 100


class SalesOrderLine(BaseModel):
    """Line item in Sales Order"""
    sales_order = models.ForeignKey(
        SalesOrder,
        on_delete=models.CASCADE,
        related_name='lines'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='so_lines'
    )
    description = models.CharField(max_length=255, blank=True)
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=1)
    quantity_delivered = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    quantity_invoiced = models.DecimalField(
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
    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00')
    )
    subtotal = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00')
    )

    class Meta:
        ordering = ['sales_order', 'id']

    def __str__(self):
        return f"{self.sales_order.reference}: {self.product.name} x {self.quantity}"

    def save(self, *args, **kwargs):
        if not self.description:
            self.description = self.product.name
        if self.unit_price == 0 and self.product.list_price:
            self.unit_price = self.product.list_price
        
        # Calculate subtotal with discount
        base_amount = self.quantity * self.unit_price
        discount = base_amount * (self.discount_percent / 100)
        self.subtotal = base_amount - discount
        
        super().save(*args, **kwargs)
        self.sales_order.compute_totals()

    @property
    def is_fully_delivered(self):
        return self.quantity_delivered >= self.quantity

    @property
    def remaining_qty(self):
        return self.quantity - self.quantity_delivered


class SalesInvoice(BaseModel):
    """Sales Invoice for billing"""
    reference = models.CharField(max_length=50, unique=True, blank=True)
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='invoices'
    )
    sales_order = models.ForeignKey(
        SalesOrder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices'
    )
    
    # Dates
    date = models.DateField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    payment_date = models.DateField(null=True, blank=True)
    
    # State
    state = models.CharField(
        max_length=20,
        choices=INVOICE_STATE_CHOICES,
        default='draft'
    )
    
    # Payment
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        blank=True
    )
    payment_reference = models.CharField(max_length=100, blank=True)
    
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
    discount_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00')
    )
    total_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00')
    )
    amount_paid = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00')
    )
    amount_due = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reference} - {self.customer.name}"

    def save(self, *args, **kwargs):
        if not self.reference:
            last_inv = SalesInvoice.objects.filter(
                reference__startswith='INV-'
            ).order_by('-reference').first()
            
            if last_inv and last_inv.reference:
                try:
                    last_num = int(last_inv.reference.split('-')[1])
                    self.reference = f'INV-{last_num + 1:05d}'
                except (ValueError, IndexError):
                    self.reference = 'INV-00001'
            else:
                self.reference = 'INV-00001'
        
        # Calculate amount due
        self.amount_due = self.total_amount - self.amount_paid
        
        super().save(*args, **kwargs)

    def compute_totals(self):
        """Compute total amounts from lines"""
        lines = self.lines.all()
        self.untaxed_amount = sum(line.subtotal for line in lines)
        self.tax_amount = self.untaxed_amount * Decimal('0.11')  # PPN 11%
        self.total_amount = self.untaxed_amount + self.tax_amount - self.discount_amount
        self.amount_due = self.total_amount - self.amount_paid
        self.save(update_fields=['untaxed_amount', 'tax_amount', 'total_amount', 'amount_due'])

    @property
    def is_overdue(self):
        if self.due_date and self.state not in ['paid', 'cancelled']:
            return timezone.now().date() > self.due_date
        return False

    @property
    def is_fully_paid(self):
        return self.amount_paid >= self.total_amount


class SalesInvoiceLine(BaseModel):
    """Line item in Sales Invoice"""
    invoice = models.ForeignKey(
        SalesInvoice,
        on_delete=models.CASCADE,
        related_name='lines'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='invoice_lines'
    )
    description = models.CharField(max_length=255, blank=True)
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=1)
    
    # Pricing
    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00')
    )
    subtotal = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal('0.00')
    )

    class Meta:
        ordering = ['invoice', 'id']

    def __str__(self):
        return f"{self.invoice.reference}: {self.product.name} x {self.quantity}"

    def save(self, *args, **kwargs):
        if not self.description:
            self.description = self.product.name
        
        # Calculate subtotal with discount
        base_amount = self.quantity * self.unit_price
        discount = base_amount * (self.discount_percent / 100)
        self.subtotal = base_amount - discount
        
        super().save(*args, **kwargs)
        self.invoice.compute_totals()
