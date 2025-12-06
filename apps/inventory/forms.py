from django import forms
from .models import Warehouse, Location, StockPicking, StockPickingLine, StockAdjustment, StockAdjustmentLine


class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ['name', 'code', 'address', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Warehouse name'
            }),
            'code': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Short code (e.g., WH01)'
            }),
            'address': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'rows': 3,
                'placeholder': 'Warehouse address'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 border-neutral-300 rounded focus:ring-blue-500'
            }),
        }


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['name', 'code', 'warehouse', 'parent', 'location_type', 'is_default', 'is_scrap', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Location name'
            }),
            'code': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Location code'
            }),
            'warehouse': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'parent': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'location_type': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'is_default': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 border-neutral-300 rounded focus:ring-blue-500'
            }),
            'is_scrap': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 border-neutral-300 rounded focus:ring-blue-500'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 border-neutral-300 rounded focus:ring-blue-500'
            }),
        }


class StockPickingForm(forms.ModelForm):
    class Meta:
        model = StockPicking
        fields = ['picking_type', 'location_src', 'location_dest', 'scheduled_date', 'origin', 'notes']
        widgets = {
            'picking_type': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'location_src': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'location_dest': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'scheduled_date': forms.DateTimeInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'type': 'datetime-local'
            }),
            'origin': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Source document reference'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'rows': 3
            }),
        }


class StockPickingLineForm(forms.ModelForm):
    class Meta:
        model = StockPickingLine
        fields = ['product', 'quantity']
        widgets = {
            'product': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'min': '0'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.products.models import Product
        self.fields['product'].queryset = Product.objects.filter(
            is_active=True,
            product_type='stockable'
        )


class StockAdjustmentForm(forms.ModelForm):
    class Meta:
        model = StockAdjustment
        fields = ['name', 'location', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Adjustment name (e.g., Monthly Inventory Count)'
            }),
            'location': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'rows': 3
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['location'].queryset = Location.objects.filter(
            is_active=True,
            location_type='internal'
        )


class StockAdjustmentLineForm(forms.ModelForm):
    class Meta:
        model = StockAdjustmentLine
        fields = ['product', 'counted_qty']
        widgets = {
            'product': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'counted_qty': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'min': '0'
            }),
        }

