import time
from django.utils import timezone

from .models import Payroll
from ..employees.models import Employee


def process_payrolls(month=None, process_existing=False):
    """
    Process payrolls for all active employees for the specified month.
    If month is not provided, uses current month.
    
    Args:
        month: The month to process payrolls for (defaults to current month)
        process_existing: If True, will process existing pending/draft payrolls. 
                         If False, only creates new payrolls.
    """
    if month is None:
        month = timezone.now().date().replace(day=1)
    
    print(f"Processing payrolls for {month.strftime('%B %Y')}")
    employees = Employee.objects.filter(is_active=True)

    for employee in employees:
        # Check if payroll already exists for this employee and month
        existing_payroll = Payroll.objects.filter(employee=employee, month=month).first()
        
        if existing_payroll:
            if process_existing:
                # Update existing payroll if it's in draft or pending status
                if existing_payroll.status in ['draft', 'pending']:
                    print(f"Processing existing payroll for {employee.full_name} - {month.strftime('%B %Y')}")
                    
                    # Update gross_salary if employee salary changed
                    if existing_payroll.gross_salary != employee.salary:
                        existing_payroll.gross_salary = employee.salary
                        existing_payroll.calculate_net_pay()
                        existing_payroll.save()
                    
                    # Change status to processing
                    existing_payroll.status = 'processing'
                    existing_payroll.save()
                    
                    # Simulate processing delay
                    time.sleep(1)
                    
                    # Change status to paid
                    existing_payroll.status = 'paid'
                    existing_payroll.payment_date = timezone.now().date()
                    existing_payroll.save()
                    
                    print(f"Payroll for {employee.full_name} processed and paid!")
                else:
                    print(f"Payroll for {employee.full_name} already processed (status: {existing_payroll.status})")
            else:
                print(f"Payroll already exists for {employee.full_name} - {month.strftime('%B %Y')} - Skipping")
            continue

        # Create new payroll for employee who doesn't have one yet
        salary = employee.salary
        print(f"Creating new payroll for employee {employee.full_name} with gross salary {salary}")
        
        # Create payroll with basic structure
        payroll = Payroll.objects.create(
            employee=employee,
            actor=employee.actor,
            gross_salary=salary,
            month=month,
            status='pending'
        )

        # Simulate processing
        time.sleep(1)
        payroll.status = 'processing'
        payroll.save()

        # Simulate payment
        time.sleep(1)
        payroll.status = 'paid'
        payroll.payment_date = timezone.now().date()
        payroll.save()

        print(f"Payroll for employee {employee.full_name} processed and paid!")