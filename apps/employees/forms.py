from django import forms
from django.contrib.auth.models import User

from .models import Employee


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            # Account (optional)
            "actor",
            # Personal Information
            "full_name",
            "date_of_birth",
            "email",
            "phone",
            # Address
            "street",
            "city",
            "state",
            "zip_code",
            "country",
            # Employment Information
            "job_title",
            "department",
            "employment_type",
            "start_date",
            "end_date",
            # Compensation
            "salary",
            # Status & Notes
            "is_active",
            "notes",
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configure actor field - filter users who don't have employee profile yet
        # self.fields['actor'].queryset = User.objects.filter(
        #     employee_profile__isnull=True
        # )
        # self.fields['actor'].required = False
        # self.fields['actor'].empty_label = "No account linked (optional)"
        # self.fields['actor'].help_text = "Link this employee to a user account (optional)"
        
        # # If editing, show current actor even if already linked
        # if self.instance and self.instance.pk and self.instance.actor:
        #     self.fields['actor'].queryset = User.objects.all()
        
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
        
        # Make employee_number read-only if editing
        if self.instance and self.instance.pk:
            if 'employee_number' in self.fields:
                self.fields['employee_number'].widget.attrs['readonly'] = True
