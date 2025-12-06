from decimal import Decimal
from django.views.generic import ListView, CreateView, UpdateView, DetailView, View
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect

from core.views import LoginRequiredMixinView
from apps.employees.models import EmployeeSetting
from .models import (
    Customer, SalesQuotation, SalesQuotationLine,
    SalesOrder, SalesOrderLine, SalesInvoice, SalesInvoiceLine
)
from .forms import (
    CustomerForm, SalesQuotationForm, SalesQuotationLineForm,
    SalesOrderForm, SalesOrderLineForm, SalesInvoiceForm, SalesInvoiceLineForm,
    PaymentForm
)
from .services import SalesService


class BaseContextMixin:
    """Mixin to add common context data"""
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_settings, created = EmployeeSetting.objects.get_or_create(actor=self.request.user)
        context["user_settings"] = user_settings
        return context


# Customer Views
class CustomerListView(LoginRequiredMixinView, BaseContextMixin, ListView):
    model = Customer
    template_name = "sales/customer_list.html"
    context_object_name = "customers"
    
    def get_queryset(self):
        queryset = Customer.objects.order_by('name')
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        customer_type = self.request.GET.get('type')
        if customer_type:
            queryset = queryset.filter(customer_type=customer_type)
        
        return queryset


class CustomerDetailView(LoginRequiredMixinView, BaseContextMixin, DetailView):
    model = Customer
    template_name = "sales/customer_detail.html"
    context_object_name = "customer"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orders'] = self.object.sales_orders.order_by('-created_at')[:10]
        context['invoices'] = self.object.invoices.order_by('-created_at')[:10]
        return context


class CustomerCreateView(LoginRequiredMixinView, BaseContextMixin, CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = "sales/customer_form.html"
    
    def form_valid(self, form):
        form.instance.actor = self.request.user
        messages.success(self.request, 'Customer created successfully.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('customer-detail', kwargs={'pk': self.object.pk})


class CustomerUpdateView(LoginRequiredMixinView, BaseContextMixin, UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = "sales/customer_form.html"
    
    def get_success_url(self):
        return reverse('customer-detail', kwargs={'pk': self.object.pk})


# Sales Quotation Views
class QuotationListView(LoginRequiredMixinView, BaseContextMixin, ListView):
    model = SalesQuotation
    template_name = "sales/quotation_list.html"
    context_object_name = "quotations"
    
    def get_queryset(self):
        queryset = SalesQuotation.objects.select_related('customer').order_by('-created_at')
        
        state = self.request.GET.get('state')
        if state:
            queryset = queryset.filter(state=state)
        
        return queryset


class QuotationDetailView(LoginRequiredMixinView, BaseContextMixin, DetailView):
    model = SalesQuotation
    template_name = "sales/quotation_detail.html"
    context_object_name = "quotation"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lines'] = self.object.lines.select_related('product', 'product__uom')
        return context


class QuotationCreateView(LoginRequiredMixinView, BaseContextMixin, CreateView):
    model = SalesQuotation
    form_class = SalesQuotationForm
    template_name = "sales/quotation_form.html"
    
    def form_valid(self, form):
        form.instance.actor = self.request.user
        messages.success(self.request, 'Quotation created successfully.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('quotation-detail', kwargs={'pk': self.object.pk})


class QuotationUpdateView(LoginRequiredMixinView, BaseContextMixin, UpdateView):
    model = SalesQuotation
    form_class = SalesQuotationForm
    template_name = "sales/quotation_form.html"
    
    def get_success_url(self):
        return reverse('quotation-detail', kwargs={'pk': self.object.pk})


class QuotationLineCreateView(LoginRequiredMixinView, BaseContextMixin, CreateView):
    model = SalesQuotationLine
    form_class = SalesQuotationLineForm
    template_name = "sales/quotation_line_form.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['quotation'] = get_object_or_404(SalesQuotation, pk=self.kwargs['quotation_pk'])
        return context
    
    def form_valid(self, form):
        form.instance.quotation = get_object_or_404(SalesQuotation, pk=self.kwargs['quotation_pk'])
        form.instance.actor = self.request.user
        messages.success(self.request, 'Line added successfully.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('quotation-detail', kwargs={'pk': self.kwargs['quotation_pk']})


class QuotationLineUpdateView(LoginRequiredMixinView, BaseContextMixin, UpdateView):
    model = SalesQuotationLine
    form_class = SalesQuotationLineForm
    template_name = "sales/quotation_line_form.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['quotation'] = self.object.quotation
        return context
    
    def get_success_url(self):
        return reverse('quotation-detail', kwargs={'pk': self.object.quotation.pk})


class QuotationLineDeleteView(LoginRequiredMixinView, View):
    def post(self, request, pk):
        line = get_object_or_404(SalesQuotationLine, pk=pk)
        quotation_pk = line.quotation.pk
        line.delete()
        messages.success(request, 'Line removed.')
        return redirect('quotation-detail', pk=quotation_pk)


class QuotationSendView(LoginRequiredMixinView, View):
    def post(self, request, pk):
        quotation = get_object_or_404(SalesQuotation, pk=pk)
        if quotation.state == 'draft':
            quotation.state = 'sent'
            quotation.save()
            messages.success(request, 'Quotation sent to customer.')
        else:
            messages.error(request, 'Only draft quotations can be sent.')
        return redirect('quotation-detail', pk=pk)


class QuotationConvertToOrderView(LoginRequiredMixinView, View):
    def post(self, request, pk):
        quotation = get_object_or_404(SalesQuotation, pk=pk)
        try:
            so = SalesService.convert_quotation_to_order(quotation)
            messages.success(request, f'Quotation converted to {so.reference}')
            return redirect('so-detail', pk=so.pk)
        except ValueError as e:
            messages.error(request, str(e))
        return redirect('quotation-detail', pk=pk)


class QuotationCancelView(LoginRequiredMixinView, View):
    def post(self, request, pk):
        quotation = get_object_or_404(SalesQuotation, pk=pk)
        if quotation.state not in ['confirmed', 'cancelled']:
            quotation.state = 'cancelled'
            quotation.save()
            messages.success(request, 'Quotation cancelled.')
        else:
            messages.error(request, 'Quotation cannot be cancelled.')
        return redirect('quotation-detail', pk=pk)


# Sales Order Views
class SOListView(LoginRequiredMixinView, BaseContextMixin, ListView):
    model = SalesOrder
    template_name = "sales/so_list.html"
    context_object_name = "orders"
    
    def get_queryset(self):
        queryset = SalesOrder.objects.select_related('customer').order_by('-created_at')
        
        state = self.request.GET.get('state')
        if state:
            queryset = queryset.filter(state=state)
        
        return queryset


class SODetailView(LoginRequiredMixinView, BaseContextMixin, DetailView):
    model = SalesOrder
    template_name = "sales/so_detail.html"
    context_object_name = "order"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lines'] = self.object.lines.select_related('product', 'product__uom')
        return context


class SOCreateView(LoginRequiredMixinView, BaseContextMixin, CreateView):
    model = SalesOrder
    form_class = SalesOrderForm
    template_name = "sales/so_form.html"
    
    def form_valid(self, form):
        form.instance.actor = self.request.user
        messages.success(self.request, 'Sales Order created.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('so-detail', kwargs={'pk': self.object.pk})


class SOUpdateView(LoginRequiredMixinView, BaseContextMixin, UpdateView):
    model = SalesOrder
    form_class = SalesOrderForm
    template_name = "sales/so_form.html"
    
    def get_success_url(self):
        return reverse('so-detail', kwargs={'pk': self.object.pk})


class SOLineCreateView(LoginRequiredMixinView, BaseContextMixin, CreateView):
    model = SalesOrderLine
    form_class = SalesOrderLineForm
    template_name = "sales/so_line_form.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = get_object_or_404(SalesOrder, pk=self.kwargs['so_pk'])
        return context
    
    def form_valid(self, form):
        form.instance.sales_order = get_object_or_404(SalesOrder, pk=self.kwargs['so_pk'])
        form.instance.actor = self.request.user
        messages.success(self.request, 'Line added.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('so-detail', kwargs={'pk': self.kwargs['so_pk']})


class SOLineDeleteView(LoginRequiredMixinView, View):
    def post(self, request, pk):
        line = get_object_or_404(SalesOrderLine, pk=pk)
        so_pk = line.sales_order.pk
        line.delete()
        messages.success(request, 'Line removed.')
        return redirect('so-detail', pk=so_pk)


class SOConfirmView(LoginRequiredMixinView, View):
    def post(self, request, pk):
        order = get_object_or_404(SalesOrder, pk=pk)
        try:
            SalesService.confirm_order(order)
            messages.success(request, 'Sales Order confirmed.')
        except ValueError as e:
            messages.error(request, str(e))
        return redirect('so-detail', pk=pk)


class SOProcessView(LoginRequiredMixinView, View):
    def post(self, request, pk):
        order = get_object_or_404(SalesOrder, pk=pk)
        try:
            SalesService.mark_order_processing(order)
            messages.success(request, 'Order is now processing.')
        except ValueError as e:
            messages.error(request, str(e))
        return redirect('so-detail', pk=pk)


class SOReadyView(LoginRequiredMixinView, View):
    def post(self, request, pk):
        order = get_object_or_404(SalesOrder, pk=pk)
        try:
            SalesService.mark_order_ready(order)
            messages.success(request, 'Order is ready.')
        except ValueError as e:
            messages.error(request, str(e))
        return redirect('so-detail', pk=pk)


class SODeliverView(LoginRequiredMixinView, View):
    def post(self, request, pk):
        order = get_object_or_404(SalesOrder, pk=pk)
        try:
            SalesService.deliver_order(order)
            messages.success(request, 'Order delivered.')
        except ValueError as e:
            messages.error(request, str(e))
        return redirect('so-detail', pk=pk)


class SOCompleteView(LoginRequiredMixinView, View):
    def post(self, request, pk):
        order = get_object_or_404(SalesOrder, pk=pk)
        try:
            SalesService.complete_order(order)
            messages.success(request, 'Order completed.')
        except ValueError as e:
            messages.error(request, str(e))
        return redirect('so-detail', pk=pk)


class SOCancelView(LoginRequiredMixinView, View):
    def post(self, request, pk):
        order = get_object_or_404(SalesOrder, pk=pk)
        try:
            SalesService.cancel_order(order)
            messages.success(request, 'Order cancelled.')
        except ValueError as e:
            messages.error(request, str(e))
        return redirect('so-detail', pk=pk)


class SOCreateInvoiceView(LoginRequiredMixinView, View):
    def post(self, request, pk):
        order = get_object_or_404(SalesOrder, pk=pk)
        try:
            invoice = SalesService.create_invoice_from_order(order)
            messages.success(request, f'Invoice {invoice.reference} created.')
            return redirect('invoice-detail', pk=invoice.pk)
        except ValueError as e:
            messages.error(request, str(e))
        return redirect('so-detail', pk=pk)


# Sales Invoice Views
class InvoiceListView(LoginRequiredMixinView, BaseContextMixin, ListView):
    model = SalesInvoice
    template_name = "sales/invoice_list.html"
    context_object_name = "invoices"
    
    def get_queryset(self):
        queryset = SalesInvoice.objects.select_related('customer', 'sales_order').order_by('-created_at')
        
        state = self.request.GET.get('state')
        if state:
            queryset = queryset.filter(state=state)
        
        return queryset


class InvoiceDetailView(LoginRequiredMixinView, BaseContextMixin, DetailView):
    model = SalesInvoice
    template_name = "sales/invoice_detail.html"
    context_object_name = "invoice"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lines'] = self.object.lines.select_related('product', 'product__uom')
        context['payment_form'] = PaymentForm(initial={'amount': self.object.amount_due})
        return context


class InvoiceCreateView(LoginRequiredMixinView, BaseContextMixin, CreateView):
    model = SalesInvoice
    form_class = SalesInvoiceForm
    template_name = "sales/invoice_form.html"
    
    def form_valid(self, form):
        form.instance.actor = self.request.user
        messages.success(self.request, 'Invoice created.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('invoice-detail', kwargs={'pk': self.object.pk})


class InvoiceUpdateView(LoginRequiredMixinView, BaseContextMixin, UpdateView):
    model = SalesInvoice
    form_class = SalesInvoiceForm
    template_name = "sales/invoice_form.html"
    
    def get_success_url(self):
        return reverse('invoice-detail', kwargs={'pk': self.object.pk})


class InvoiceLineCreateView(LoginRequiredMixinView, BaseContextMixin, CreateView):
    model = SalesInvoiceLine
    form_class = SalesInvoiceLineForm
    template_name = "sales/invoice_line_form.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['invoice'] = get_object_or_404(SalesInvoice, pk=self.kwargs['invoice_pk'])
        return context
    
    def form_valid(self, form):
        form.instance.invoice = get_object_or_404(SalesInvoice, pk=self.kwargs['invoice_pk'])
        form.instance.actor = self.request.user
        messages.success(self.request, 'Line added.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('invoice-detail', kwargs={'pk': self.kwargs['invoice_pk']})


class InvoiceLineDeleteView(LoginRequiredMixinView, View):
    def post(self, request, pk):
        line = get_object_or_404(SalesInvoiceLine, pk=pk)
        invoice_pk = line.invoice.pk
        line.delete()
        messages.success(request, 'Line removed.')
        return redirect('invoice-detail', pk=invoice_pk)


class InvoiceSendView(LoginRequiredMixinView, View):
    def post(self, request, pk):
        invoice = get_object_or_404(SalesInvoice, pk=pk)
        if invoice.state == 'draft':
            invoice.state = 'sent'
            invoice.save()
            messages.success(request, 'Invoice sent to customer.')
        else:
            messages.error(request, 'Only draft invoices can be sent.')
        return redirect('invoice-detail', pk=pk)


class InvoicePaymentView(LoginRequiredMixinView, View):
    def post(self, request, pk):
        invoice = get_object_or_404(SalesInvoice, pk=pk)
        form = PaymentForm(request.POST)
        
        if form.is_valid():
            try:
                SalesService.record_payment(
                    invoice,
                    amount=form.cleaned_data['amount'],
                    payment_method=form.cleaned_data['payment_method'],
                    payment_reference=form.cleaned_data.get('payment_reference', '')
                )
                messages.success(request, 'Payment recorded.')
            except ValueError as e:
                messages.error(request, str(e))
        else:
            messages.error(request, 'Invalid payment data.')
        
        return redirect('invoice-detail', pk=pk)


class InvoiceCancelView(LoginRequiredMixinView, View):
    def post(self, request, pk):
        invoice = get_object_or_404(SalesInvoice, pk=pk)
        try:
            SalesService.cancel_invoice(invoice)
            messages.success(request, 'Invoice cancelled.')
        except ValueError as e:
            messages.error(request, str(e))
        return redirect('invoice-detail', pk=pk)
