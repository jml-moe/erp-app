from django.contrib import admin
from .models import (
    Warehouse, Location, StockQuant, StockMove, 
    StockPicking, StockPickingLine, StockAdjustment, StockAdjustmentLine
)


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'warehouse', 'location_type', 'is_default', 'is_active')
    list_filter = ('warehouse', 'location_type', 'is_default', 'is_active')
    search_fields = ('name', 'code')


@admin.register(StockQuant)
class StockQuantAdmin(admin.ModelAdmin):
    list_display = ('product', 'location', 'quantity', 'reserved_quantity', 'available_quantity', 'unit_cost')
    list_filter = ('location__warehouse', 'location')
    search_fields = ('product__name', 'product__internal_reference')


@admin.register(StockMove)
class StockMoveAdmin(admin.ModelAdmin):
    list_display = ('reference', 'product', 'location_src', 'location_dest', 'quantity', 'quantity_done', 'state')
    list_filter = ('state', 'move_type', 'location_src', 'location_dest')
    search_fields = ('reference', 'product__name', 'origin')


class StockPickingLineInline(admin.TabularInline):
    model = StockPickingLine
    extra = 1


@admin.register(StockPicking)
class StockPickingAdmin(admin.ModelAdmin):
    list_display = ('reference', 'picking_type', 'location_src', 'location_dest', 'state', 'scheduled_date')
    list_filter = ('picking_type', 'state')
    search_fields = ('reference', 'origin')
    inlines = [StockPickingLineInline]


class StockAdjustmentLineInline(admin.TabularInline):
    model = StockAdjustmentLine
    extra = 1


@admin.register(StockAdjustment)
class StockAdjustmentAdmin(admin.ModelAdmin):
    list_display = ('reference', 'name', 'location', 'state', 'date')
    list_filter = ('state', 'location')
    search_fields = ('reference', 'name')
    inlines = [StockAdjustmentLineInline]

