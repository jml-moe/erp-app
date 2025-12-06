from django import forms
from .models import BillOfMaterials, BOMLine, ManufacturingOrder
from apps.products.models import Product
from apps.inventory.models import Location


class BOMForm(forms.ModelForm):
    class Meta:
        model = BillOfMaterials
        fields = ['product', 'reference', 'quantity', 'bom_type', 'ready_time', 'is_active', 'notes']
        widgets = {
            'product': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'reference': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Auto-generated if empty'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'min': '0.01'
            }),
            'bom_type': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'ready_time': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'min': '0'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 border-neutral-300 rounded focus:ring-blue-500'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'rows': 3
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter to products that can be sold (finished products)
        self.fields['product'].queryset = Product.objects.filter(
            is_active=True,
            can_be_sold=True
        )
        self.fields['reference'].required = False


class BOMLineForm(forms.ModelForm):
    class Meta:
        model = BOMLine
        fields = ['product', 'quantity', 'uom', 'notes']
        widgets = {
            'product': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'step': '0.0001',
                'min': '0.0001'
            }),
            'uom': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'notes': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Optional notes'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter to stockable/consumable products (raw materials)
        self.fields['product'].queryset = Product.objects.filter(
            is_active=True
        ).exclude(product_type='service')
        self.fields['uom'].required = False


class ManufacturingOrderForm(forms.ModelForm):
    class Meta:
        model = ManufacturingOrder
        fields = ['product', 'bom', 'quantity', 'source_location', 'destination_location', 
                  'scheduled_date', 'priority', 'origin', 'notes']
        widgets = {
            'product': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'bom': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'min': '0.01'
            }),
            'source_location': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'destination_location': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'scheduled_date': forms.DateTimeInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'type': 'datetime-local'
            }),
            'priority': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'origin': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'e.g., SO-00001'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'rows': 3
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.filter(
            is_active=True,
            can_be_sold=True
        )
        self.fields['bom'].queryset = BillOfMaterials.objects.filter(is_active=True)
        self.fields['source_location'].queryset = Location.objects.filter(
            is_active=True,
            location_type='internal'
        )
        self.fields['destination_location'].queryset = Location.objects.filter(
            is_active=True,
            location_type='internal'
        )
        self.fields['bom'].required = False


class ProduceForm(forms.Form):
    """Form for recording production output"""
    quantity = forms.DecimalField(
        min_value=0.01,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
            'step': '0.01'
        })
    )

