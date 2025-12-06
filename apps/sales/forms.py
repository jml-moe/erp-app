from django import forms
from .models import (
    Customer, SalesQuotation, SalesQuotationLine,
    SalesOrder, SalesOrderLine, SalesInvoice, SalesInvoiceLine
)


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            'name', 'customer_type', 'email', 'phone', 'mobile',
            'address', 'city', 'company_name', 'tax_id', 'notes', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Customer name'}),
            'customer_type': forms.Select(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'email@example.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Phone number'}),
            'mobile': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Mobile number'}),
            'address': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'City'}),
            'company_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Company name'}),
            'tax_id': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'NPWP'}),
            'notes': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }


class SalesQuotationForm(forms.ModelForm):
    class Meta:
        model = SalesQuotation
        fields = ['customer', 'validity_date', 'discount_amount', 'notes']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-input'}),
            'validity_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'discount_amount': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
        }


class SalesQuotationLineForm(forms.ModelForm):
    class Meta:
        model = SalesQuotationLine
        fields = ['product', 'description', 'quantity', 'unit_price', 'discount_percent']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-input line-product'}),
            'description': forms.TextInput(attrs={'class': 'form-input'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0.01'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'discount_percent': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0', 'max': '100'}),
        }


class SalesOrderForm(forms.ModelForm):
    class Meta:
        model = SalesOrder
        fields = ['customer', 'expected_date', 'source_location', 'discount_amount', 'notes']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-input'}),
            'expected_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'source_location': forms.Select(attrs={'class': 'form-input'}),
            'discount_amount': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
        }


class SalesOrderLineForm(forms.ModelForm):
    class Meta:
        model = SalesOrderLine
        fields = ['product', 'description', 'quantity', 'unit_price', 'discount_percent']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-input line-product'}),
            'description': forms.TextInput(attrs={'class': 'form-input'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0.01'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'discount_percent': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0', 'max': '100'}),
        }


class SalesInvoiceForm(forms.ModelForm):
    class Meta:
        model = SalesInvoice
        fields = ['customer', 'sales_order', 'due_date', 'discount_amount', 'notes']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-input'}),
            'sales_order': forms.Select(attrs={'class': 'form-input'}),
            'due_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'discount_amount': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
        }


class SalesInvoiceLineForm(forms.ModelForm):
    class Meta:
        model = SalesInvoiceLine
        fields = ['product', 'description', 'quantity', 'unit_price', 'discount_percent']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-input line-product'}),
            'description': forms.TextInput(attrs={'class': 'form-input'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0.01'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'discount_percent': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0', 'max': '100'}),
        }


class PaymentForm(forms.Form):
    """Form for recording invoice payment"""
    amount = forms.DecimalField(
        max_digits=14, 
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0.01'})
    )
    payment_method = forms.ChoiceField(
        choices=[
            ('cash', 'Cash'),
            ('bank_transfer', 'Bank Transfer'),
            ('credit_card', 'Credit Card'),
            ('debit_card', 'Debit Card'),
            ('e_wallet', 'E-Wallet'),
            ('qris', 'QRIS'),
        ],
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    payment_reference = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Reference number'})
    )

