from django.contrib import admin

from .models import Employee, EmployeeSetting


@admin.register(EmployeeSetting)
class EmployeeSettingAdmin(admin.ModelAdmin):
    list_display = ('actor', 'role', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('actor__username', 'actor__email')


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        'employee_number',
        'full_name',
        'job_title',
        'department',
        'employment_type',
        'salary',
        'is_active',
        'start_date',
    )
    list_filter = (
        'is_active',
        'department',
        'employment_type',
        'start_date',
    )
    search_fields = (
        'employee_number',
        'full_name',
        'email',
        'phone',
        'job_title',
    )
    readonly_fields = ('employee_number', 'created_at', 'updated_at', 'id')
    fieldsets = (
        ('Identification', {
            'fields': ('employee_number', 'actor', 'id')
        }),
        ('Personal Information', {
            'fields': ('full_name', 'date_of_birth', 'email', 'phone')
        }),
        ('Address', {
            'fields': ('street', 'city', 'state', 'zip_code', 'country'),
            'classes': ('collapse',)
        }),
        ('Employment Information', {
            'fields': ('job_title', 'department', 'employment_type', 'start_date', 'end_date')
        }),
        ('Compensation', {
            'fields': ('salary',)
        }),
        ('Status & Notes', {
            'fields': ('is_active', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    ordering = ('-created_at',)
