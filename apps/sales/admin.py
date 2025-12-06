from django.contrib import admin
from .models import (
    Customer, SalesQuotation, SalesQuotationLine,
    SalesOrder, SalesOrderLine, SalesInvoice, SalesInvoiceLine
)


class SalesQuotationLineInline(admin.TabularInline):
    model = SalesQuotationLine
    extra = 1


class SalesOrderLineInline(admin.TabularInline):
    model = SalesOrderLine
    extra = 1


class SalesInvoiceLineInline(admin.TabularInline):
    model = SalesInvoiceLine
    extra = 1


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'customer_type', 'phone', 'email', 'is_active')
    list_filter = ('customer_type', 'is_active', 'city')
    search_fields = ('name', 'company_name', 'email', 'phone')


@admin.register(SalesQuotation)
class SalesQuotationAdmin(admin.ModelAdmin):
    list_display = ('reference', 'customer', 'date', 'state', 'total_amount')
    list_filter = ('state', 'date')
    search_fields = ('reference', 'customer__name')
    inlines = [SalesQuotationLineInline]


@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):
    list_display = ('reference', 'customer', 'date', 'state', 'total_amount')
    list_filter = ('state', 'date')
    search_fields = ('reference', 'customer__name')
    inlines = [SalesOrderLineInline]


@admin.register(SalesInvoice)
class SalesInvoiceAdmin(admin.ModelAdmin):
    list_display = ('reference', 'customer', 'date', 'state', 'total_amount', 'amount_paid', 'amount_due')
    list_filter = ('state', 'date', 'payment_method')
    search_fields = ('reference', 'customer__name')
    inlines = [SalesInvoiceLineInline]
