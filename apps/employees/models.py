from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from core.models import BaseModel

ROLE_CHOICES = (
    ('user', 'User'),
    ('manager', 'Manager'),
)

EMPLOYMENT_TYPE_CHOICES = (
    ('full_time', 'Full Time'),
    ('part_time', 'Part Time'),
    ('contract', 'Contract'),
    ('intern', 'Intern'),
)

DEPARTMENT_CHOICES = (
    ('hr', 'Human Resources'),
    ('finance', 'Finance & Accounting'),
    ('it', 'Information Technology'),
    ('sales', 'Sales & Marketing'),
    ('operations', 'Operations'),
    ('manufacturing', 'Manufacturing'),
    ('purchasing', 'Purchasing'),
    ('warehouse', 'Warehouse'),
    ('general', 'General'),
)


class EmployeeSetting(BaseModel):
    actor = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=120, choices=ROLE_CHOICES, default='user')

    def __str__(self):
        return f"{self.actor.username} - {self.get_role_display()}"


class Employee(BaseModel):
    """Employee master data for ERP system"""
    # Employee Identification
    employee_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        help_text='Auto-generated employee ID'
    )
    actor = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employee_profile'
    )
    
    # Personal Information
    full_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    
    # Address Information
    street = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default='Indonesia')
    
    # Employment Information
    job_title = models.CharField(max_length=255)
    department = models.CharField(
        max_length=50,
        choices=DEPARTMENT_CHOICES,
        default='general'
    )
    employment_type = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_TYPE_CHOICES,
        default='full_time'
    )
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    
    # Compensation
    salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Monthly salary'
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, help_text='Additional notes about the employee')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'

    def __str__(self):
        if self.employee_number:
            return f"[{self.employee_number}] {self.full_name}"
        return self.full_name

    def save(self, *args, **kwargs):
        # Auto-generate employee number if not provided
        if not self.employee_number:
            # Generate format: EMP-YYYY-XXXXX (e.g., EMP-2024-00123)
            year = timezone.now().year
            last_employee = Employee.objects.filter(
                employee_number__startswith=f'EMP-{year}'
            ).order_by('-employee_number').first()
            
            if last_employee and last_employee.employee_number:
                try:
                    last_num = int(last_employee.employee_number.split('-')[-1])
                    new_num = last_num + 1
                except (ValueError, IndexError):
                    new_num = 1
            else:
                new_num = 1
            
            self.employee_number = f'EMP-{year}-{str(new_num).zfill(5)}'
        
        super().save(*args, **kwargs)

    def get_years_of_service(self):
        """Calculate years of service"""
        if self.end_date:
            delta = self.end_date - self.start_date
        else:
            delta = timezone.now().date() - self.start_date
        return round(delta.days / 365.25, 1)
