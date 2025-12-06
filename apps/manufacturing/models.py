from django.db import models
from decimal import Decimal
from django.utils import timezone

from core.models import BaseModel
from apps.products.models import Product, UnitOfMeasure
from apps.inventory.models import Location


BOM_TYPE_CHOICES = (
    ('normal', 'Manufacture this product'),
    ('kit', 'Kit / Package'),
)

MO_STATE_CHOICES = (
    ('draft', 'Draft'),
    ('confirmed', 'Confirmed'),
    ('in_progress', 'In Progress'),
    ('done', 'Done'),
    ('cancelled', 'Cancelled'),
)


class BillOfMaterials(BaseModel):
    """Bill of Materials - Recipe/Formula for producing a product"""
    
    # The product being produced
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='boms',
        help_text='Product to be manufactured'
    )
    
    # Reference/Name
    reference = models.CharField(max_length=100, blank=True)
    
    # Quantity produced by this BOM
    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('1.00'),
        help_text='Quantity of product produced by this BOM'
    )
    
    # BOM Type
    bom_type = models.CharField(
        max_length=20,
        choices=BOM_TYPE_CHOICES,
        default='normal'
    )
    
    # Ready time (production time in minutes)
    ready_time = models.PositiveIntegerField(
        default=0,
        help_text='Production time in minutes'
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Notes
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Bill of Materials'
        verbose_name_plural = 'Bills of Materials'
        ordering = ['product__name']

    def __str__(self):
        return f"BOM: {self.product.name}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"BOM-{self.product.internal_reference or self.product.name[:20]}"
        super().save(*args, **kwargs)

    @property
    def total_cost(self):
        """Calculate total cost of components"""
        return sum(line.cost for line in self.lines.all())

    @property
    def component_count(self):
        """Number of components in this BOM"""
        return self.lines.count()


class BOMLine(BaseModel):
    """Component line in a Bill of Materials"""
    
    bom = models.ForeignKey(
        BillOfMaterials,
        on_delete=models.CASCADE,
        related_name='lines'
    )
    
    # Component product
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='bom_lines',
        help_text='Component/ingredient product'
    )
    
    # Quantity needed
    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        help_text='Quantity of component needed'
    )
    
    # Unit of measure (can differ from product's default UoM)
    uom = models.ForeignKey(
        UnitOfMeasure,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        help_text='Leave empty to use product default UoM'
    )
    
    # Notes for this component
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['bom', 'id']

    def __str__(self):
        return f"{self.bom.product.name}: {self.product.name} x {self.quantity}"

    @property
    def display_uom(self):
        """Return the UoM to use"""
        return self.uom or self.product.uom

    @property
    def cost(self):
        """Calculate cost of this component"""
        return self.quantity * self.product.standard_price


class ManufacturingOrder(BaseModel):
    """Manufacturing Order / Work Order for production"""
    
    reference = models.CharField(max_length=50, unique=True, blank=True)
    
    # Product to produce
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='manufacturing_orders'
    )
    
    # BOM used
    bom = models.ForeignKey(
        BillOfMaterials,
        on_delete=models.SET_NULL,
        null=True,
        related_name='manufacturing_orders'
    )
    
    # Quantities
    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text='Quantity to produce'
    )
    quantity_produced = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Quantity actually produced'
    )
    
    # Locations
    source_location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        related_name='mo_source',
        help_text='Location to consume components from'
    )
    destination_location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        related_name='mo_destination',
        help_text='Location to store finished product'
    )
    
    # State
    state = models.CharField(
        max_length=20,
        choices=MO_STATE_CHOICES,
        default='draft'
    )
    
    # Dates
    scheduled_date = models.DateTimeField(null=True, blank=True)
    date_started = models.DateTimeField(null=True, blank=True)
    date_finished = models.DateTimeField(null=True, blank=True)
    
    # Origin (e.g., from Sales Order)
    origin = models.CharField(max_length=100, blank=True)
    
    # Priority
    PRIORITY_CHOICES = (
        ('0', 'Not Urgent'),
        ('1', 'Normal'),
        ('2', 'Urgent'),
        ('3', 'Very Urgent'),
    )
    priority = models.CharField(
        max_length=1,
        choices=PRIORITY_CHOICES,
        default='1'
    )
    
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Manufacturing Order'
        verbose_name_plural = 'Manufacturing Orders'

    def __str__(self):
        return f"{self.reference}: {self.product.name} x {self.quantity}"

    def save(self, *args, **kwargs):
        if not self.reference:
            last_mo = ManufacturingOrder.objects.filter(
                reference__startswith='MO-'
            ).order_by('-reference').first()
            
            if last_mo and last_mo.reference:
                try:
                    last_num = int(last_mo.reference.split('-')[1])
                    self.reference = f'MO-{last_num + 1:05d}'
                except (ValueError, IndexError):
                    self.reference = 'MO-00001'
            else:
                self.reference = 'MO-00001'
        
        super().save(*args, **kwargs)

    @property
    def progress_percentage(self):
        """Calculate production progress"""
        if self.quantity == 0:
            return 0
        return (self.quantity_produced / self.quantity) * 100

    @property
    def expected_cost(self):
        """Calculate expected production cost"""
        if self.bom:
            return self.bom.total_cost * self.quantity
        return Decimal('0.00')


class ManufacturingOrderLine(BaseModel):
    """Component consumption line in Manufacturing Order"""
    
    manufacturing_order = models.ForeignKey(
        ManufacturingOrder,
        on_delete=models.CASCADE,
        related_name='lines'
    )
    
    # Component product
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='mo_lines'
    )
    
    # Quantities
    quantity_required = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        help_text='Required quantity based on BOM'
    )
    quantity_consumed = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal('0.00'),
        help_text='Actually consumed quantity'
    )
    
    # UoM
    uom = models.ForeignKey(
        UnitOfMeasure,
        on_delete=models.PROTECT,
        null=True
    )

    class Meta:
        ordering = ['manufacturing_order', 'id']

    def __str__(self):
        return f"{self.manufacturing_order.reference}: {self.product.name}"

    @property
    def is_fully_consumed(self):
        return self.quantity_consumed >= self.quantity_required

    @property
    def remaining_qty(self):
        return self.quantity_required - self.quantity_consumed

