from django.contrib import admin

from .models import Payroll


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = (
        'employee',
        'month',
        'gross_salary',
        'tax_deduction',
        'insurance_deduction',
        'other_deduction',
        'net_pay',
        'status',
        'payment_date',
    )
    list_filter = (
        'status',
        'month',
        'payment_date',
        'created_at',
    )
    search_fields = (
        'employee__full_name',
        'employee__employee_number',
        'month',
    )
    readonly_fields = ('net_pay', 'created_at', 'updated_at', 'id')
    fieldsets = (
        ('Employee & Period', {
            'fields': ('employee', 'month', 'id')
        }),
        ('Earnings', {
            'fields': ('gross_salary',)
        }),
        ('Deductions', {
            'fields': ('tax_deduction', 'insurance_deduction', 'other_deduction')
        }),
        ('Net Pay', {
            'fields': ('net_pay',)
        }),
        ('Status & Payment', {
            'fields': ('status', 'payment_date')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    ordering = ('-month', '-created_at')
    
    def save_model(self, request, obj, form, change):
        # Recalculate net pay on save
        obj.calculate_net_pay()
        if not obj.actor:
            obj.actor = request.user
        super().save_model(request, obj, form, change)
