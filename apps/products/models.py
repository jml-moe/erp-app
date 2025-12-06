from django.db import models
from decimal import Decimal

from core.models import BaseModel


class Category(BaseModel):
    """Product category for organizing products"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='children'
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} / {self.name}"
        return self.name

    def get_full_path(self):
        """Get full category path"""
        if self.parent:
            return f"{self.parent.get_full_path()} / {self.name}"
        return self.name


class UnitOfMeasure(BaseModel):
    """Unit of measure for products"""
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=10)
    category = models.CharField(
        max_length=20,
        choices=(
            ('unit', 'Unit'),
            ('weight', 'Weight'),
            ('volume', 'Volume'),
            ('length', 'Length'),
            ('time', 'Time'),
        ),
        default='unit'
    )
    # Conversion factor relative to base unit in same category
    ratio = models.DecimalField(
        max_digits=12, 
        decimal_places=6, 
        default=Decimal('1.000000'),
        help_text='Conversion ratio to base unit'
    )
    is_base_unit = models.BooleanField(
        default=False,
        help_text='Is this the base unit for its category?'
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Unit of Measure'
        verbose_name_plural = 'Units of Measure'
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} ({self.symbol})"


PRODUCT_TYPE_CHOICES = (
    ('consumable', 'Consumable'),  # Not tracked in stock
    ('stockable', 'Stockable'),    # Tracked in stock
    ('service', 'Service'),        # No stock, e.g. delivery fee
)

COST_METHOD_CHOICES = (
    ('standard', 'Standard Price'),
    ('average', 'Average Cost'),
    ('fifo', 'First In First Out'),
)


class Product(BaseModel):
    """Master product data"""
    # Basic info
    name = models.CharField(max_length=255)
    internal_reference = models.CharField(
        max_length=50, 
        unique=True, 
        blank=True, 
        null=True,
        help_text='Internal code/SKU'
    )
    barcode = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True)
    
    # Classification
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='products'
    )
    product_type = models.CharField(
        max_length=20, 
        choices=PRODUCT_TYPE_CHOICES, 
        default='stockable'
    )
    
    # Units
    uom = models.ForeignKey(
        UnitOfMeasure,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name='Unit of Measure',
        help_text='Default unit for stock and sales'
    )
    purchase_uom = models.ForeignKey(
        UnitOfMeasure,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='purchase_products',
        verbose_name='Purchase Unit of Measure',
        help_text='Unit used when purchasing (if different)'
    )
    
    # Pricing
    cost_method = models.CharField(
        max_length=20,
        choices=COST_METHOD_CHOICES,
        default='average'
    )
    standard_price = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text='Cost price'
    )
    list_price = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text='Sales price'
    )
    
    # Inventory
    can_be_purchased = models.BooleanField(default=True)
    can_be_sold = models.BooleanField(default=True)
    reorder_point = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text='Minimum stock level before reorder'
    )
    reorder_qty = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text='Default quantity to reorder'
    )
    
    # Status
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        if self.internal_reference:
            return f"[{self.internal_reference}] {self.name}"
        return self.name

    def save(self, *args, **kwargs):
        # Auto-generate internal reference if not provided
        if not self.internal_reference:
            # Get the last product with auto-generated reference
            last_product = Product.objects.filter(
                internal_reference__startswith='PROD-'
            ).order_by('-internal_reference').first()
            
            if last_product and last_product.internal_reference:
                try:
                    last_num = int(last_product.internal_reference.split('-')[1])
                    self.internal_reference = f'PROD-{last_num + 1:05d}'
                except (ValueError, IndexError):
                    self.internal_reference = 'PROD-00001'
            else:
                self.internal_reference = 'PROD-00001'
        
        super().save(*args, **kwargs)

    @property
    def display_uom(self):
        """Return the purchase UOM if set, otherwise the default UOM"""
        return self.purchase_uom or self.uom

