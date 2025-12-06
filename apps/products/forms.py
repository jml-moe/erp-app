from django import forms
from .models import Category, UnitOfMeasure, Product


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'parent', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Category name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Description',
                'rows': 3
            }),
            'parent': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 border-neutral-300 rounded focus:ring-blue-500'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Exclude self from parent choices to prevent circular reference
        if self.instance.pk:
            self.fields['parent'].queryset = Category.objects.exclude(pk=self.instance.pk)


class UnitOfMeasureForm(forms.ModelForm):
    class Meta:
        model = UnitOfMeasure
        fields = ['name', 'symbol', 'category', 'ratio', 'is_base_unit', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Unit name (e.g., Kilogram)'
            }),
            'symbol': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Symbol (e.g., kg)'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'ratio': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'step': '0.000001'
            }),
            'is_base_unit': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 border-neutral-300 rounded focus:ring-blue-500'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 border-neutral-300 rounded focus:ring-blue-500'
            }),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'internal_reference', 'barcode', 'description',
            'category', 'product_type',
            'uom', 'purchase_uom',
            'cost_method', 'standard_price', 'list_price',
            'can_be_purchased', 'can_be_sold', 'reorder_point', 'reorder_qty',
            'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Product name'
            }),
            'internal_reference': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Auto-generated if empty'
            }),
            'barcode': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Barcode'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Product description',
                'rows': 3
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'product_type': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'uom': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'purchase_uom': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'cost_method': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'standard_price': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'step': '0.01'
            }),
            'list_price': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'step': '0.01'
            }),
            'can_be_purchased': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 border-neutral-300 rounded focus:ring-blue-500'
            }),
            'can_be_sold': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 border-neutral-300 rounded focus:ring-blue-500'
            }),
            'reorder_point': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'step': '0.01'
            }),
            'reorder_qty': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'step': '0.01'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 border-neutral-300 rounded focus:ring-blue-500'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['internal_reference'].required = False
        self.fields['purchase_uom'].required = False
        self.fields['category'].required = False

