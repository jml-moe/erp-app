from django.db import models
from django.utils import timezone
from decimal import Decimal

from core.models import BaseModel
from apps.employees.models import Employee

PAYROLL_STATUS_CHOICES = (
    ('draft', 'Draft'),
    ('pending', 'Pending'),
    ('processing', 'Processing'),
    ('paid', 'Paid'),
    ('cancelled', 'Cancelled'),
)


class Payroll(BaseModel):
    """Payroll record for employee compensation"""
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="payrolls",
        null=True,
        blank=True,
        verbose_name='Employee'
    )
    
    # Period
    month = models.DateField(
        default=timezone.now,
        help_text='Payroll period (month/year)'
    )
    
    # Earnings
    gross_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Gross salary amount'
    )
    
    # Deductions
    tax_deduction = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Income tax deduction'
    )
    insurance_deduction = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Insurance deduction (BPJS, etc.)'
    )
    other_deduction = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Other deductions'
    )
    
    # Net Pay (calculated)
    net_pay = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text='Net pay after deductions'
    )
    
    # Status and Dates
    status = models.CharField(
        max_length=100,
        choices=PAYROLL_STATUS_CHOICES,
        default='draft'
    )
    payment_date = models.DateField(
        null=True,
        blank=True,
        help_text='Date when payroll was paid'
    )
    
    # Notes
    notes = models.TextField(blank=True, help_text='Additional notes')

    class Meta:
        ordering = ['-month', '-created_at']
        verbose_name = 'Payroll'
        verbose_name_plural = 'Payrolls'
        # Prevent duplicate payroll for same employee and month
        unique_together = [['employee', 'month']]

    def __str__(self):
        if self.employee:
            month_str = self.month.strftime('%B %Y')
            return f"{self.employee.full_name} - {month_str}"
        return f"Payroll - {self.month.strftime('%B %Y')}"

    def calculate_net_pay(self):
        """Calculate net pay from gross salary minus all deductions"""
        total_deductions = (
            self.tax_deduction +
            self.insurance_deduction +
            self.other_deduction
        )
        self.net_pay = max(Decimal('0'), self.gross_salary - total_deductions)
        return self.net_pay

    def save(self, *args, **kwargs):
        # Auto-calculate net pay
        if not self.gross_salary:
            # If gross salary is not set, use employee's salary
            if self.employee and self.employee.salary:
                self.gross_salary = self.employee.salary
        
        # Calculate net pay
        self.calculate_net_pay()
        
        # Set payment date when status changes to paid
        if self.status == 'paid' and not self.payment_date:
            self.payment_date = timezone.now().date()
        
        super().save(*args, **kwargs)
