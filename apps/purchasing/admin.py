from django.contrib import admin
from .models import RequestForQuotation, RFQLine, PurchaseOrder, POLine


class RFQLineInline(admin.TabularInline):
    model = RFQLine
    extra = 1


@admin.register(RequestForQuotation)
class RequestForQuotationAdmin(admin.ModelAdmin):
    list_display = ('reference', 'vendor', 'date', 'state', 'total_amount')
    list_filter = ('state', 'vendor', 'date')
    search_fields = ('reference', 'vendor__name')
    readonly_fields = ('untaxed_amount', 'tax_amount', 'total_amount')
    inlines = [RFQLineInline]


class POLineInline(admin.TabularInline):
    model = POLine
    extra = 1


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('reference', 'vendor', 'date', 'state', 'total_amount', 'received_percentage')
    list_filter = ('state', 'vendor', 'date')
    search_fields = ('reference', 'vendor__name')
    readonly_fields = ('untaxed_amount', 'tax_amount', 'total_amount')
    inlines = [POLineInline]

