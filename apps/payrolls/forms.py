from django import forms

from .models import Payroll


class PayrollForm(forms.ModelForm):
    class Meta:
        model = Payroll
        fields = ["employee", "month", "amount", "status"]
        widgets = {
            "month": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update(
                {"class": "w-full rounded-lg border border-neutral-200 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"}
            )
