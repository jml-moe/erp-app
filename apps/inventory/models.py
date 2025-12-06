from django.db import models
from decimal import Decimal

from core.models import BaseModel
from apps.products.models import Product


LOCATION_TYPE_CHOICES = (
    ('internal', 'Internal Location'),
    ('supplier', 'Supplier Location'),
    ('customer', 'Customer Location'),
    ('inventory', 'Inventory Loss'),
    ('production', 'Production'),
    ('transit', 'Transit Location'),
)

STOCK_MOVE_STATE_CHOICES = (
    ('draft', 'Draft'),
    ('waiting', 'Waiting'),
    ('confirmed', 'Confirmed'),
    ('assigned', 'Available'),
    ('done', 'Done'),
    ('cancelled', 'Cancelled'),
)

STOCK_MOVE_TYPE_CHOICES = (
    ('incoming', 'Incoming'),
    ('outgoing', 'Outgoing'),
    ('internal', 'Internal Transfer'),
)

VALUATION_METHOD_CHOICES = (
    ('standard', 'Standard Price'),
    ('average', 'Average Cost'),
    ('fifo', 'First In First Out'),
)


class Warehouse(BaseModel):
    """Warehouse/Storage location"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"[{self.code}] {self.name}"

    @property
    def stock_location(self):
        """Get the main stock location for this warehouse"""
        return self.locations.filter(location_type='internal', is_default=True).first()


class Location(BaseModel):
    """Storage location within a warehouse"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='locations',
        null=True,
        blank=True
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    location_type = models.CharField(
        max_length=20,
        choices=LOCATION_TYPE_CHOICES,
        default='internal'
    )
    is_default = models.BooleanField(
        default=False,
        help_text='Default stock location for warehouse'
    )
    is_scrap = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['warehouse', 'name']
        unique_together = ['warehouse', 'code']

    def __str__(self):
        if self.warehouse:
            return f"{self.warehouse.code}/{self.code}"
        return self.code

    @property
    def full_name(self):
        """Get full location path"""
        parts = []
        if self.warehouse:
            parts.append(self.warehouse.name)
        if self.parent:
            parts.append(self.parent.name)
        parts.append(self.name)
        return ' / '.join(parts)


class StockQuant(BaseModel):
    """Current stock quantity per product per location"""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='stock_quants'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name='stock_quants'
    )
    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    reserved_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Quantity reserved for outgoing moves'
    )
    # For FIFO valuation
    unit_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    incoming_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['product', 'location', 'incoming_date']

    def __str__(self):
        return f"{self.product.name} @ {self.location}: {self.quantity}"

    @property
    def available_quantity(self):
        """Quantity available (not reserved)"""
        return self.quantity - self.reserved_quantity

    @property
    def total_value(self):
        """Total value of this quant"""
        return self.quantity * self.unit_cost


class StockMove(BaseModel):
    """Stock movement record"""
    reference = models.CharField(max_length=50, blank=True)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='stock_moves'
    )
    
    # Locations
    location_src = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name='moves_from',
        verbose_name='Source Location'
    )
    location_dest = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name='moves_to',
        verbose_name='Destination Location'
    )
    
    # Quantities
    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text='Quantity to move'
    )
    quantity_done = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Actually moved quantity'
    )
    
    # Pricing
    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # State
    state = models.CharField(
        max_length=20,
        choices=STOCK_MOVE_STATE_CHOICES,
        default='draft'
    )
    move_type = models.CharField(
        max_length=20,
        choices=STOCK_MOVE_TYPE_CHOICES,
        default='internal'
    )
    
    # Dates
    scheduled_date = models.DateTimeField(null=True, blank=True)
    date_done = models.DateTimeField(null=True, blank=True)
    
    # Related documents
    origin = models.CharField(
        max_length=100,
        blank=True,
        help_text='Source document reference (e.g., PO-0001)'
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reference or self.id}: {self.product.name} ({self.quantity})"

    def save(self, *args, **kwargs):
        # Auto-generate reference
        if not self.reference:
            last_move = StockMove.objects.filter(
                reference__startswith='SM-'
            ).order_by('-reference').first()
            
            if last_move and last_move.reference:
                try:
                    last_num = int(last_move.reference.split('-')[1])
                    self.reference = f'SM-{last_num + 1:06d}'
                except (ValueError, IndexError):
                    self.reference = 'SM-000001'
            else:
                self.reference = 'SM-000001'
        
        # Determine move type
        if self.location_src.location_type == 'supplier':
            self.move_type = 'incoming'
        elif self.location_dest.location_type == 'customer':
            self.move_type = 'outgoing'
        else:
            self.move_type = 'internal'
        
        super().save(*args, **kwargs)


class StockPicking(BaseModel):
    """Group of stock moves (like a delivery order or receipt)"""
    PICKING_TYPE_CHOICES = (
        ('incoming', 'Receipt'),
        ('outgoing', 'Delivery'),
        ('internal', 'Internal Transfer'),
    )
    
    STATE_CHOICES = (
        ('draft', 'Draft'),
        ('waiting', 'Waiting'),
        ('ready', 'Ready'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    )
    
    reference = models.CharField(max_length=50, unique=True, blank=True)
    picking_type = models.CharField(
        max_length=20,
        choices=PICKING_TYPE_CHOICES,
        default='incoming'
    )
    
    # Default locations
    location_src = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        related_name='pickings_from',
        verbose_name='Source Location'
    )
    location_dest = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        related_name='pickings_to',
        verbose_name='Destination Location'
    )
    
    # State and dates
    state = models.CharField(
        max_length=20,
        choices=STATE_CHOICES,
        default='draft'
    )
    scheduled_date = models.DateTimeField(null=True, blank=True)
    date_done = models.DateTimeField(null=True, blank=True)
    
    # Related document
    origin = models.CharField(
        max_length=100,
        blank=True,
        help_text='Source document reference'
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Stock Picking'
        verbose_name_plural = 'Stock Pickings'

    def __str__(self):
        return self.reference or f"Picking-{self.id}"

    def save(self, *args, **kwargs):
        if not self.reference:
            prefix = {
                'incoming': 'IN',
                'outgoing': 'OUT',
                'internal': 'INT'
            }.get(self.picking_type, 'PICK')
            
            last_picking = StockPicking.objects.filter(
                reference__startswith=f'{prefix}-'
            ).order_by('-reference').first()
            
            if last_picking and last_picking.reference:
                try:
                    last_num = int(last_picking.reference.split('-')[1])
                    self.reference = f'{prefix}-{last_num + 1:05d}'
                except (ValueError, IndexError):
                    self.reference = f'{prefix}-00001'
            else:
                self.reference = f'{prefix}-00001'
        
        super().save(*args, **kwargs)


class StockPickingLine(BaseModel):
    """Line item in a stock picking"""
    picking = models.ForeignKey(
        StockPicking,
        on_delete=models.CASCADE,
        related_name='lines'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='picking_lines'
    )
    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    quantity_done = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    # Override locations from picking if needed
    location_src = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='picking_lines_from'
    )
    location_dest = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='picking_lines_to'
    )
    
    # Link to actual stock move
    stock_move = models.OneToOneField(
        StockMove,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='picking_line'
    )

    class Meta:
        ordering = ['picking', 'product']

    def __str__(self):
        return f"{self.picking.reference}: {self.product.name} x {self.quantity}"

    @property
    def source_location(self):
        return self.location_src or self.picking.location_src

    @property
    def destination_location(self):
        return self.location_dest or self.picking.location_dest


class StockAdjustment(BaseModel):
    """Inventory adjustment/count"""
    STATE_CHOICES = (
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    )
    
    reference = models.CharField(max_length=50, unique=True, blank=True)
    name = models.CharField(max_length=255)
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name='adjustments'
    )
    state = models.CharField(
        max_length=20,
        choices=STATE_CHOICES,
        default='draft'
    )
    date = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.reference or self.name

    def save(self, *args, **kwargs):
        if not self.reference:
            last_adj = StockAdjustment.objects.filter(
                reference__startswith='ADJ-'
            ).order_by('-reference').first()
            
            if last_adj and last_adj.reference:
                try:
                    last_num = int(last_adj.reference.split('-')[1])
                    self.reference = f'ADJ-{last_num + 1:05d}'
                except (ValueError, IndexError):
                    self.reference = 'ADJ-00001'
            else:
                self.reference = 'ADJ-00001'
        
        super().save(*args, **kwargs)


class StockAdjustmentLine(BaseModel):
    """Line item in stock adjustment"""
    adjustment = models.ForeignKey(
        StockAdjustment,
        on_delete=models.CASCADE,
        related_name='lines'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='adjustment_lines'
    )
    theoretical_qty = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='System quantity before adjustment'
    )
    counted_qty = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Actual counted quantity'
    )
    difference = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )

    class Meta:
        ordering = ['adjustment', 'product']
        unique_together = ['adjustment', 'product']

    def __str__(self):
        return f"{self.adjustment.reference}: {self.product.name}"

    def save(self, *args, **kwargs):
        self.difference = self.counted_qty - self.theoretical_qty
        super().save(*args, **kwargs)

