from decimal import Decimal
from django.db import models
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView, View, FormView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseRedirect

from core.views import LoginRequiredMixinView
from apps.employees.models import EmployeeSetting
from .models import RequestForQuotation, RFQLine, PurchaseOrder, POLine
from .forms import RFQForm, RFQLineForm, POForm, POLineForm, ReceiveProductsForm, ConvertRFQForm, POBillingForm, POPaymentForm
from .services import RFQService, POService


class BaseContextMixin:
    """Mixin to add common context data"""
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_settings, created = EmployeeSetting.objects.get_or_create(actor=self.request.user)
        context["user_settings"] = user_settings
        return context


# RFQ Views
class RFQListView(LoginRequiredMixinView, BaseContextMixin, ListView):
    model = RequestForQuotation
    template_name = "purchasing/rfq_list.html"
    context_object_name = "rfqs"
    
    def get_queryset(self):
        queryset = RequestForQuotation.objects.select_related('vendor').order_by('-created_at')
        
        state = self.request.GET.get('state')
        if state:
            queryset = queryset.filter(state=state)
        
        return queryset


class RFQDetailView(LoginRequiredMixinView, BaseContextMixin, DetailView):
    model = RequestForQuotation
    template_name = "purchasing/rfq_detail.html"
    context_object_name = "rfq"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lines'] = self.object.lines.select_related('product', 'product__uom')
        context['convert_form'] = ConvertRFQForm()
        return context


class RFQCreateView(LoginRequiredMixinView, BaseContextMixin, CreateView):
    model = RequestForQuotation
    form_class = RFQForm
    template_name = "purchasing/rfq_form.html"
    
    def form_valid(self, form):
        form.instance.actor = self.request.user
        messages.success(self.request, 'RFQ created successfully.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('rfq-detail', kwargs={'pk': self.object.pk})


class RFQUpdateView(LoginRequiredMixinView, BaseContextMixin, UpdateView):
    model = RequestForQuotation
    form_class = RFQForm
    template_name = "purchasing/rfq_form.html"
    
    def get_success_url(self):
        return reverse('rfq-detail', kwargs={'pk': self.object.pk})


class RFQLineCreateView(LoginRequiredMixinView, BaseContextMixin, CreateView):
    model = RFQLine
    form_class = RFQLineForm
    template_name = "purchasing/rfq_line_form.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rfq'] = get_object_or_404(RequestForQuotation, pk=self.kwargs['rfq_pk'])
        return context
    
    def form_valid(self, form):
        form.instance.rfq = get_object_or_404(RequestForQuotation, pk=self.kwargs['rfq_pk'])
        form.instance.actor = self.request.user
        messages.success(self.request, 'Line added successfully.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('rfq-detail', kwargs={'pk': self.kwargs['rfq_pk']})


class RFQLineUpdateView(LoginRequiredMixinView, BaseContextMixin, UpdateView):
    model = RFQLine
    form_class = RFQLineForm
    template_name = "purchasing/rfq_line_form.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rfq'] = self.object.rfq
        return context
    
    def get_success_url(self):
        return reverse('rfq-detail', kwargs={'pk': self.object.rfq.pk})


class RFQLineDeleteView(LoginRequiredMixinView, View):
    def post(self, request, pk):
        line = get_object_or_404(RFQLine, pk=pk)
        rfq_pk = line.rfq.pk
        line.delete()
        messages.success(request, 'Line removed.')
        return redirect('rfq-detail', pk=rfq_pk)


class RFQSendView(LoginRequiredMixinView, View):
    def post(self, request, pk):
        rfq = get_object_or_404(RequestForQuotation, pk=pk)
        try:
            RFQService.send_rfq(rfq)
            messages.success(request, 'RFQ sent to vendor.')
        except ValueError as e:
            messages.error(request, str(e))
        return redirect('rfq-detail', pk=pk)


class RFQReceiveQuotationView(LoginRequiredMixinView, View):
    def post(self, request, pk):
        rfq = get_object_or_404(RequestForQuotation, pk=pk)
        try:
            RFQService.receive_quotation(rfq)
            messages.success(request, 'Quotation marked as received.')
        except ValueError as e:
            messages.error(request, str(e))
        return redirect('rfq-detail', pk=pk)


class RFQConvertToPOView(LoginRequiredMixinView, View):
    def post(self, request, pk):
        rfq = get_object_or_404(RequestForQuotation, pk=pk)
        form = ConvertRFQForm(request.POST)
        
        if form.is_valid():
            try:
                po = RFQService.convert_to_po(
                    rfq,
                    delivery_location=form.cleaned_data['delivery_location'],
                    user=request.user
                )
                messages.success(request, f'RFQ converted to {po.reference}')
                return redirect('po-detail', pk=po.pk)
            except ValueError as e:
                messages.error(request, str(e))
        else:
            messages.error(request, 'Please select a delivery location.')
        
        return redirect('rfq-detail', pk=pk)


class RFQCancelView(LoginRequiredMixinView, View):
    def post(self, request, pk):
        rfq = get_object_or_404(RequestForQuotation, pk=pk)
        try:
            RFQService.cancel_rfq(rfq)
            messages.success(request, 'RFQ cancelled.')
        except ValueError as e:
            messages.error(request, str(e))
        return redirect('rfq-detail', pk=pk)


# Purchase Order Views
class POListView(LoginRequiredMixinView, BaseContextMixin, ListView):
    model = PurchaseOrder
    template_name = "purchasing/po_list.html"
    context_object_name = "pos"
    
    def get_queryset(self):
        queryset = PurchaseOrder.objects.select_related('vendor').order_by('-created_at')
        
        state = self.request.GET.get('state')
        if state:
            queryset = queryset.filter(state=state)
        
        return queryset


class PODetailView(LoginRequiredMixinView, BaseContextMixin, DetailView):
    model = PurchaseOrder
    template_name = "purchasing/po_detail.html"
    context_object_name = "po"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lines'] = self.object.lines.select_related('product', 'product__uom')
        context['receive_form'] = ReceiveProductsForm(po=self.object)
        return context


class POCreateView(LoginRequiredMixinView, BaseContextMixin, CreateView):
    model = PurchaseOrder
    form_class = POForm
    template_name = "purchasing/po_form.html"
    
    def form_valid(self, form):
        form.instance.actor = self.request.user
        messages.success(self.request, 'Purchase Order created.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('po-detail', kwargs={'pk': self.object.pk})


class POUpdateView(LoginRequiredMixinView, BaseContextMixin, UpdateView):
    model = PurchaseOrder
    form_class = POForm
    template_name = "purchasing/po_form.html"
    
    def get_success_url(self):
        return reverse('po-detail', kwargs={'pk': self.object.pk})


class POLineCreateView(LoginRequiredMixinView, BaseContextMixin, CreateView):
    model = POLine
    form_class = POLineForm
    template_name = "purchasing/po_line_form.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['po'] = get_object_or_404(PurchaseOrder, pk=self.kwargs['po_pk'])
        return context
    
    def form_valid(self, form):
        form.instance.purchase_order = get_object_or_404(PurchaseOrder, pk=self.kwargs['po_pk'])
        form.instance.actor = self.request.user
        messages.success(self.request, 'Line added.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('po-detail', kwargs={'pk': self.kwargs['po_pk']})


class POLineDeleteView(LoginRequiredMixinView, View):
    def post(self, request, pk):
        line = get_object_or_404(POLine, pk=pk)
        po_pk = line.purchase_order.pk
        line.delete()
        messages.success(request, 'Line removed.')
        return redirect('po-detail', pk=po_pk)


class POConfirmView(LoginRequiredMixinView, View):
    def post(self, request, pk):
        po = get_object_or_404(PurchaseOrder, pk=pk)
        try:
            POService.confirm_po(po)
            messages.success(request, 'Purchase Order confirmed.')
        except ValueError as e:
            messages.error(request, str(e))
        return redirect('po-detail', pk=pk)


class POSendView(LoginRequiredMixinView, View):
    def post(self, request, pk):
        po = get_object_or_404(PurchaseOrder, pk=pk)
        try:
            POService.send_po(po)
            messages.success(request, 'Purchase Order sent to vendor.')
        except ValueError as e:
            messages.error(request, str(e))
        return redirect('po-detail', pk=pk)


class POReceiveView(LoginRequiredMixinView, View):
    def post(self, request, pk):
        po = get_object_or_404(PurchaseOrder, pk=pk)
        form = ReceiveProductsForm(request.POST, po=po)
        
        if form.is_valid():
            try:
                received_quantities = {}
                for field_name, qty in form.cleaned_data.items():
                    if field_name.startswith('line_') and qty > 0:
                        line_id = field_name.replace('line_', '')
                        received_quantities[line_id] = qty
                
                if received_quantities:
                    POService.receive_products(po, received_quantities, user=request.user)
                    messages.success(request, 'Products received successfully.')
                else:
                    messages.warning(request, 'No quantities specified.')
            except ValueError as e:
                messages.error(request, str(e))
        else:
            messages.error(request, 'Invalid quantities.')
        
        return redirect('po-detail', pk=pk)


class POMarkBilledView(LoginRequiredMixinView, View):
    def get(self, request, pk):
        po = get_object_or_404(PurchaseOrder, pk=pk)
        form = POBillingForm(initial={
            'bill_amount': po.total_amount
        })

        context = {
            'po': po,
            'form': form,
        }
        user_settings, _ = EmployeeSetting.objects.get_or_create(actor=request.user)
        context["user_settings"] = user_settings

        return render(request, 'purchasing/po_billing_form.html', context)

    def post(self, request, pk):
        po = get_object_or_404(PurchaseOrder, pk=pk)
        form = POBillingForm(request.POST)

        if form.is_valid():
            try:
                POService.mark_billed(
                    po,
                    bill_reference=form.cleaned_data['bill_reference'],
                    bill_date=form.cleaned_data['bill_date'],
                    bill_amount=form.cleaned_data['bill_amount']
                )
                messages.success(request, 'Purchase Order marked as billed.')
                return redirect('po-detail', pk=pk)
            except ValueError as e:
                messages.error(request, str(e))
        else:
            messages.error(request, 'Invalid form data.')

        context = {
            'po': po,
            'form': form,
        }
        user_settings, _ = EmployeeSetting.objects.get_or_create(actor=request.user)
        context["user_settings"] = user_settings

        return render(request, 'purchasing/po_billing_form.html', context)


class POMarkDoneView(LoginRequiredMixinView, View):
    def get(self, request, pk):
        po = get_object_or_404(PurchaseOrder, pk=pk)
        form = POPaymentForm()

        context = {
            'po': po,
            'form': form,
        }
        user_settings, _ = EmployeeSetting.objects.get_or_create(actor=request.user)
        context["user_settings"] = user_settings

        return render(request, 'purchasing/po_payment_form.html', context)

    def post(self, request, pk):
        po = get_object_or_404(PurchaseOrder, pk=pk)
        form = POPaymentForm(request.POST)

        if form.is_valid():
            try:
                POService.record_payment(
                    po,
                    payment_date=form.cleaned_data['payment_date'],
                    payment_reference=form.cleaned_data.get('payment_reference', '')
                )
                messages.success(request, 'Payment recorded and Purchase Order completed.')
                return redirect('po-detail', pk=pk)
            except ValueError as e:
                messages.error(request, str(e))
        else:
            messages.error(request, 'Invalid form data.')

        context = {
            'po': po,
            'form': form,
        }
        user_settings, _ = EmployeeSetting.objects.get_or_create(actor=request.user)
        context["user_settings"] = user_settings

        return render(request, 'purchasing/po_payment_form.html', context)


class POCancelView(LoginRequiredMixinView, View):
    def post(self, request, pk):
        po = get_object_or_404(PurchaseOrder, pk=pk)
        try:
            POService.cancel_po(po)
            messages.success(request, 'Purchase Order cancelled.')
        except ValueError as e:
            messages.error(request, str(e))
        return redirect('po-detail', pk=pk)

