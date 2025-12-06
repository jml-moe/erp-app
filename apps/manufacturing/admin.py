from django.contrib import admin
from .models import BillOfMaterials, BOMLine, ManufacturingOrder, ManufacturingOrderLine


class BOMLineInline(admin.TabularInline):
    model = BOMLine
    extra = 1


@admin.register(BillOfMaterials)
class BillOfMaterialsAdmin(admin.ModelAdmin):
    list_display = ('reference', 'product', 'quantity', 'bom_type', 'component_count', 'total_cost', 'is_active')
    list_filter = ('bom_type', 'is_active')
    search_fields = ('reference', 'product__name')
    inlines = [BOMLineInline]


class ManufacturingOrderLineInline(admin.TabularInline):
    model = ManufacturingOrderLine
    extra = 0


@admin.register(ManufacturingOrder)
class ManufacturingOrderAdmin(admin.ModelAdmin):
    list_display = ('reference', 'product', 'quantity', 'quantity_produced', 'state', 'priority', 'scheduled_date')
    list_filter = ('state', 'priority')
    search_fields = ('reference', 'product__name', 'origin')
    inlines = [ManufacturingOrderLineInline]

