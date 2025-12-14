from django import forms

from .models import Payroll
from apps.employees.models import Employee


class PayrollForm(forms.ModelForm):
    class Meta:
        model = Payroll
        fields = [
            "employee",
            "month",
            "gross_salary",
            "tax_deduction",
            "insurance_deduction",
            "other_deduction",
            "status",
            "payment_date",
            "notes",
        ]
        widgets = {
            "month": forms.DateInput(attrs={"type": "date"}),
            "payment_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter active employees only
        self.fields['employee'].queryset = Employee.objects.filter(is_active=True)
        self.fields['employee'].empty_label = "Select Employee"
        
        # Apply styling to all fields
        base_attrs = {
            "class": "w-full rounded-lg border border-neutral-200 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        }
        
        for field in self.fields.values():
            if field.widget.__class__.__name__ != 'Textarea':
                field.widget.attrs.update(base_attrs)
            else:
                field.widget.attrs.update({
                    "class": "w-full rounded-lg border border-neutral-200 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                })
        
        # Make net_pay read-only (calculated field)
        if 'net_pay' in self.fields:
            self.fields['net_pay'].widget.attrs.update({
                'readonly': True,
                'class': base_attrs['class'] + ' bg-neutral-50'
            })

    def clean(self):
        cleaned_data = super().clean()
        employee = cleaned_data.get('employee')
        
        # Auto-fill gross_salary from employee if not provided
        if employee and employee.salary and not cleaned_data.get('gross_salary'):
            cleaned_data['gross_salary'] = employee.salary
        
        return cleaned_data
