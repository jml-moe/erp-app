from django import forms
from .models import RequestForQuotation, RFQLine, PurchaseOrder, POLine
from apps.vendors.models import Vendor
from apps.products.models import Product
from apps.inventory.models import Location


class RFQForm(forms.ModelForm):
    class Meta:
        model = RequestForQuotation
        fields = ['vendor', 'deadline', 'notes']
        widgets = {
            'vendor': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'deadline': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'rows': 3
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vendor'].queryset = Vendor.objects.filter(is_active=True)


class RFQLineForm(forms.ModelForm):
    class Meta:
        model = RFQLine
        fields = ['product', 'description', 'quantity', 'unit_price']
        widgets = {
            'product': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'description': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Auto-filled from product if empty'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'min': '0.01'
            }),
            'unit_price': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'min': '0'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.filter(
            is_active=True,
            can_be_purchased=True
        )
        self.fields['description'].required = False


class POForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['vendor', 'expected_date', 'delivery_location', 'notes']
        widgets = {
            'vendor': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'expected_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'type': 'date'
            }),
            'delivery_location': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'rows': 3
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vendor'].queryset = Vendor.objects.filter(is_active=True)
        self.fields['delivery_location'].queryset = Location.objects.filter(
            is_active=True,
            location_type='internal'
        )


class POLineForm(forms.ModelForm):
    class Meta:
        model = POLine
        fields = ['product', 'description', 'quantity', 'unit_price']
        widgets = {
            'product': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'description': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Auto-filled from product if empty'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'min': '0.01'
            }),
            'unit_price': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'min': '0'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.filter(
            is_active=True,
            can_be_purchased=True
        )
        self.fields['description'].required = False


class ReceiveProductsForm(forms.Form):
    """Dynamic form for receiving products"""
    
    def __init__(self, *args, po=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        if po:
            for line in po.lines.all():
                remaining = line.quantity - line.quantity_received
                if remaining > 0:
                    self.fields[f'line_{line.id}'] = forms.DecimalField(
                        label=f"{line.product.name}",
                        initial=remaining,
                        min_value=0,
                        max_value=remaining,
                        widget=forms.NumberInput(attrs={
                            'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                            'step': '0.01'
                        })
                    )


class ConvertRFQForm(forms.Form):
    """Form for converting RFQ to PO"""
    delivery_location = forms.ModelChoiceField(
        queryset=Location.objects.filter(is_active=True, location_type='internal'),
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
        })
    )

