from django import forms
from .models import Vendor, VendorContact, VendorProduct


class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = [
            'name', 'code', 'company_name',
            'email', 'phone', 'website',
            'street', 'street2', 'city', 'state', 'zip_code', 'country',
            'tax_id', 'payment_term',
            'rating', 'notes',
            'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Vendor name'
            }),
            'code': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Auto-generated if empty'
            }),
            'company_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Legal company name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'email@example.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': '+62...'
            }),
            'website': forms.URLInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'https://...'
            }),
            'street': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Street address'
            }),
            'street2': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Apartment, suite, etc.'
            }),
            'city': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'City'
            }),
            'state': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Province/State'
            }),
            'zip_code': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'ZIP/Postal code'
            }),
            'country': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Country'
            }),
            'tax_id': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'NPWP'
            }),
            'payment_term': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'rating': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Additional notes',
                'rows': 3
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 border-neutral-300 rounded focus:ring-blue-500'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['code'].required = False


class VendorContactForm(forms.ModelForm):
    class Meta:
        model = VendorContact
        fields = ['name', 'title', 'email', 'phone', 'mobile', 'is_primary', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Contact name'
            }),
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Job title'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'email@example.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Phone'
            }),
            'mobile': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Mobile'
            }),
            'is_primary': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 border-neutral-300 rounded focus:ring-blue-500'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'rows': 2
            }),
        }


class VendorProductForm(forms.ModelForm):
    class Meta:
        model = VendorProduct
        fields = [
            'product', 'vendor_product_code', 'vendor_product_name',
            'price', 'currency', 'min_qty', 'lead_time_days',
            'is_preferred', 'is_active'
        ]
        widgets = {
            'product': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'vendor_product_code': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': "Vendor's product code"
            }),
            'vendor_product_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': "Vendor's product name"
            }),
            'price': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'step': '0.01'
            }),
            'currency': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'min_qty': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'step': '0.01'
            }),
            'lead_time_days': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'
            }),
            'is_preferred': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 border-neutral-300 rounded focus:ring-blue-500'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 border-neutral-300 rounded focus:ring-blue-500'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter to only show purchasable products
        from apps.products.models import Product
        self.fields['product'].queryset = Product.objects.filter(
            is_active=True,
            can_be_purchased=True
        )

