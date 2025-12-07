from django.db import models
from django.utils import timezone

from core.models import BaseModel
from apps.employees.models import Employee

PAYROLL_STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('processing', 'Processing'),
    ('paid', 'Paid'),
)

class Payroll(BaseModel):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="payrolls",
        null=True,
        blank=True,
    )
    month = models.DateField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=100, choices=PAYROLL_STATUS_CHOICES, default='pending')
