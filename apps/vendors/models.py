from django.db import models
from decimal import Decimal

from core.models import BaseModel
from apps.products.models import Product


PAYMENT_TERM_CHOICES = (
    ('cod', 'Cash on Delivery'),
    ('net7', 'Net 7 Days'),
    ('net14', 'Net 14 Days'),
    ('net30', 'Net 30 Days'),
    ('net60', 'Net 60 Days'),
)

VENDOR_RATING_CHOICES = (
    (1, '1 - Poor'),
    (2, '2 - Below Average'),
    (3, '3 - Average'),
    (4, '4 - Good'),
    (5, '5 - Excellent'),
)


class Vendor(BaseModel):
    """Supplier/Vendor master data"""
    # Basic info
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True)
    
    # Contact info
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    
    # Address
    street = models.CharField(max_length=255, blank=True)
    street2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default='Indonesia')
    
    # Business info
    tax_id = models.CharField(max_length=50, blank=True, verbose_name='NPWP')
    payment_term = models.CharField(
        max_length=20,
        choices=PAYMENT_TERM_CHOICES,
        default='net30'
    )
    
    # Rating and notes
    rating = models.IntegerField(
        choices=VENDOR_RATING_CHOICES,
        default=3
    )
    notes = models.TextField(blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        if self.code:
            return f"[{self.code}] {self.name}"
        return self.name

    def save(self, *args, **kwargs):
        # Auto-generate code if not provided
        if not self.code:
            last_vendor = Vendor.objects.filter(
                code__startswith='VND-'
            ).order_by('-code').first()
            
            if last_vendor and last_vendor.code:
                try:
                    last_num = int(last_vendor.code.split('-')[1])
                    self.code = f'VND-{last_num + 1:04d}'
                except (ValueError, IndexError):
                    self.code = 'VND-0001'
            else:
                self.code = 'VND-0001'
        
        super().save(*args, **kwargs)

    @property
    def full_address(self):
        """Return formatted full address"""
        parts = [self.street]
        if self.street2:
            parts.append(self.street2)
        if self.city:
            city_part = self.city
            if self.state:
                city_part += f", {self.state}"
            if self.zip_code:
                city_part += f" {self.zip_code}"
            parts.append(city_part)
        if self.country:
            parts.append(self.country)
        return '\n'.join(filter(None, parts))

    @property
    def total_products(self):
        """Return count of products supplied by this vendor"""
        return self.vendor_products.count()


class VendorContact(BaseModel):
    """Additional contacts for a vendor"""
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name='contacts'
    )
    name = models.CharField(max_length=255)
    title = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    mobile = models.CharField(max_length=20, blank=True)
    is_primary = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-is_primary', 'name']

    def __str__(self):
        return f"{self.name} ({self.vendor.name})"

    def save(self, *args, **kwargs):
        # If this is set as primary, unset other primaries
        if self.is_primary:
            VendorContact.objects.filter(
                vendor=self.vendor,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)


class VendorProduct(BaseModel):
    """Products supplied by a vendor with vendor-specific pricing"""
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name='vendor_products'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='vendor_products'
    )
    
    # Vendor-specific info
    vendor_product_code = models.CharField(
        max_length=50,
        blank=True,
        help_text="Product code used by this vendor"
    )
    vendor_product_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Product name used by this vendor"
    )
    
    # Pricing
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Price from this vendor"
    )
    currency = models.CharField(max_length=3, default='IDR')
    min_qty = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('1.00'),
        help_text="Minimum order quantity"
    )
    
    # Lead time
    lead_time_days = models.PositiveIntegerField(
        default=1,
        help_text="Delivery lead time in days"
    )
    
    # Status
    is_preferred = models.BooleanField(
        default=False,
        help_text="Preferred vendor for this product"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['vendor', 'product']
        ordering = ['vendor', 'product']

    def __str__(self):
        return f"{self.vendor.name} - {self.product.name}"

    def save(self, *args, **kwargs):
        # If this is set as preferred, unset other preferred for this product
        if self.is_preferred:
            VendorProduct.objects.filter(
                product=self.product,
                is_preferred=True
            ).exclude(pk=self.pk).update(is_preferred=False)
        super().save(*args, **kwargs)

