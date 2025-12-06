from django.contrib import admin
from .models import Category, UnitOfMeasure, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'is_active', 'created_at')
    list_filter = ('is_active', 'parent')
    search_fields = ('name', 'description')
    ordering = ('name',)


@admin.register(UnitOfMeasure)
class UnitOfMeasureAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol', 'category', 'ratio', 'is_base_unit', 'is_active')
    list_filter = ('category', 'is_base_unit', 'is_active')
    search_fields = ('name', 'symbol')
    ordering = ('category', 'name')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 
        'internal_reference', 
        'category', 
        'product_type', 
        'uom',
        'standard_price',
        'list_price',
        'is_active'
    )
    list_filter = ('product_type', 'category', 'is_active', 'can_be_purchased', 'can_be_sold')
    search_fields = ('name', 'internal_reference', 'barcode', 'description')
    ordering = ('name',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'internal_reference', 'barcode', 'description')
        }),
        ('Classification', {
            'fields': ('category', 'product_type')
        }),
        ('Units of Measure', {
            'fields': ('uom', 'purchase_uom')
        }),
        ('Pricing', {
            'fields': ('cost_method', 'standard_price', 'list_price')
        }),
        ('Inventory', {
            'fields': ('can_be_purchased', 'can_be_sold', 'reorder_point', 'reorder_qty')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

