from django.contrib import admin
from .models import Vendor, VendorContact, VendorProduct


class VendorContactInline(admin.TabularInline):
    model = VendorContact
    extra = 1


class VendorProductInline(admin.TabularInline):
    model = VendorProduct
    extra = 1


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'email', 'phone', 'payment_term', 'rating', 'is_active')
    list_filter = ('is_active', 'payment_term', 'rating', 'country')
    search_fields = ('name', 'code', 'email', 'company_name')
    ordering = ('name',)
    inlines = [VendorContactInline, VendorProductInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'company_name')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'website')
        }),
        ('Address', {
            'fields': ('street', 'street2', 'city', 'state', 'zip_code', 'country')
        }),
        ('Business Information', {
            'fields': ('tax_id', 'payment_term')
        }),
        ('Rating & Notes', {
            'fields': ('rating', 'notes')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


@admin.register(VendorContact)
class VendorContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'vendor', 'title', 'email', 'phone', 'is_primary')
    list_filter = ('is_primary', 'vendor')
    search_fields = ('name', 'email', 'vendor__name')


@admin.register(VendorProduct)
class VendorProductAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'product', 'price', 'min_qty', 'lead_time_days', 'is_preferred', 'is_active')
    list_filter = ('is_preferred', 'is_active', 'vendor')
    search_fields = ('vendor__name', 'product__name', 'vendor_product_code')

