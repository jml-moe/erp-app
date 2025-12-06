from decimal import Decimal
from django.db import models
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView, View
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect

from core.views import LoginRequiredMixinView
from apps.employees.models import EmployeeSetting
from .models import BillOfMaterials, BOMLine, ManufacturingOrder, ManufacturingOrderLine
from .forms import BOMForm, BOMLineForm, ManufacturingOrderForm, ProduceForm
from .services import BOMService, ManufacturingService


class BaseContextMixin:
    """Mixin to add common context data"""
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_settings, created = EmployeeSetting.objects.get_or_create(actor=self.request.user)
        context["user_settings"] = user_settings
        return context


# BOM Views
class BOMListView(LoginRequiredMixinView, BaseContextMixin, ListView):
    model = BillOfMaterials
    template_name = "manufacturing/bom_list.html"
    context_object_name = "boms"
    
    def get_queryset(self):
        queryset = BillOfMaterials.objects.select_related('product').prefetch_related('lines')
        
        active_only = self.request.GET.get('active', 'true')
        if active_only == 'true':
            queryset = queryset.filter(is_active=True)
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(reference__icontains=search) |
                models.Q(product__name__icontains=search)
            )
        
        return queryset


class BOMDetailView(LoginRequiredMixinView, BaseContextMixin, DetailView):
    model = BillOfMaterials
    template_name = "manufacturing/bom_detail.html"
    context_object_name = "bom"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lines'] = self.object.lines.select_related('product', 'product__uom', 'uom')
        return context


class BOMCreateView(LoginRequiredMixinView, BaseContextMixin, CreateView):
    model = BillOfMaterials
    form_class = BOMForm
    template_name = "manufacturing/bom_form.html"
    
    def form_valid(self, form):
        form.instance.actor = self.request.user
        messages.success(self.request, 'Bill of Materials created successfully.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('bom-detail', kwargs={'pk': self.object.pk})


class BOMUpdateView(LoginRequiredMixinView, BaseContextMixin, UpdateView):
    model = BillOfMaterials
    form_class = BOMForm
    template_name = "manufacturing/bom_form.html"
    
    def form_valid(self, form):
        messages.success(self.request, 'Bill of Materials updated successfully.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('bom-detail', kwargs={'pk': self.object.pk})


class BOMDeleteView(LoginRequiredMixinView, BaseContextMixin, DeleteView):
    model = BillOfMaterials
    template_name = "manufacturing/bom_confirm_delete.html"
    success_url = reverse_lazy('bom-list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Bill of Materials deleted successfully.')
        return super().delete(request, *args, **kwargs)


# BOM Line Views
class BOMLineCreateView(LoginRequiredMixinView, BaseContextMixin, CreateView):
    model = BOMLine
    form_class = BOMLineForm
    template_name = "manufacturing/bom_line_form.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['bom'] = get_object_or_404(BillOfMaterials, pk=self.kwargs['bom_pk'])
        return context
    
    def form_valid(self, form):
        form.instance.bom = get_object_or_404(BillOfMaterials, pk=self.kwargs['bom_pk'])
        form.instance.actor = self.request.user
        messages.success(self.request, 'Component added successfully.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('bom-detail', kwargs={'pk': self.kwargs['bom_pk']})


class BOMLineUpdateView(LoginRequiredMixinView, BaseContextMixin, UpdateView):
    model = BOMLine
    form_class = BOMLineForm
    template_name = "manufacturing/bom_line_form.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['bom'] = self.object.bom
        return context
    
    def get_success_url(self):
        return reverse('bom-detail', kwargs={'pk': self.object.bom.pk})


class BOMLineDeleteView(LoginRequiredMixinView, View):
    def post(self, request, pk):
        line = get_object_or_404(BOMLine, pk=pk)
        bom_pk = line.bom.pk
        line.delete()
        messages.success(request, 'Component removed.')
        return redirect('bom-detail', pk=bom_pk)


# Manufacturing Order Views
class MOListView(LoginRequiredMixinView, BaseContextMixin, ListView):
    model = ManufacturingOrder
    template_name = "manufacturing/mo_list.html"
    context_object_name = "orders"
    
    def get_queryset(self):
        queryset = ManufacturingOrder.objects.select_related('product', 'bom').order_by('-created_at')
        
        state = self.request.GET.get('state')
        if state:
            queryset = queryset.filter(state=state)
        
        priority = self.request.GET.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        return queryset


class MODetailView(LoginRequiredMixinView, BaseContextMixin, DetailView):
    model = ManufacturingOrder
    template_name = "manufacturing/mo_detail.html"
    context_object_name = "mo"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lines'] = self.object.lines.select_related('product', 'product__uom', 'uom')
        
        # Calculate remaining quantity
        remaining_quantity = self.object.quantity - self.object.quantity_produced
        context['remaining_quantity'] = remaining_quantity
        context['produce_form'] = ProduceForm(initial={
            'quantity': remaining_quantity
        })
        
        # Check component availability
        if self.object.bom and self.object.source_location:
            context['availability'] = BOMService.check_component_availability(
                self.object.bom,
                self.object.quantity,
                self.object.source_location
            )
        
        return context


class MOCreateView(LoginRequiredMixinView, BaseContextMixin, CreateView):
    model = ManufacturingOrder
    form_class = ManufacturingOrderForm
    template_name = "manufacturing/mo_form.html"
    
    def form_valid(self, form):
        form.instance.actor = self.request.user
        response = super().form_valid(form)
        
        # Create lines from BOM if selected
        if self.object.bom:
            for bom_line in self.object.bom.lines.all():
                ManufacturingOrderLine.objects.create(
                    manufacturing_order=self.object,
                    product=bom_line.product,
                    quantity_required=bom_line.quantity * self.object.quantity,
                    uom=bom_line.display_uom,
                    actor=self.request.user
                )
        
        messages.success(self.request, 'Manufacturing Order created successfully.')
        return response
    
    def get_success_url(self):
        return reverse('mo-detail', kwargs={'pk': self.object.pk})


class MOUpdateView(LoginRequiredMixinView, BaseContextMixin, UpdateView):
    model = ManufacturingOrder
    form_class = ManufacturingOrderForm
    template_name = "manufacturing/mo_form.html"
    
    def get_success_url(self):
        return reverse('mo-detail', kwargs={'pk': self.object.pk})


# MO Action Views
class MOConfirmView(LoginRequiredMixinView, View):
    def post(self, request, pk):
        mo = get_object_or_404(ManufacturingOrder, pk=pk)
        try:
            ManufacturingService.confirm_mo(mo)
            messages.success(request, 'Manufacturing Order confirmed.')
        except ValueError as e:
            messages.error(request, str(e))
        return redirect('mo-detail', pk=pk)


class MOStartView(LoginRequiredMixinView, View):
    def post(self, request, pk):
        mo = get_object_or_404(ManufacturingOrder, pk=pk)
        try:
            ManufacturingService.start_production(mo)
            messages.success(request, 'Production started.')
        except ValueError as e:
            messages.error(request, str(e))
        return redirect('mo-detail', pk=pk)


class MOConsumeView(LoginRequiredMixinView, View):
    def post(self, request, pk):
        mo = get_object_or_404(ManufacturingOrder, pk=pk)
        try:
            ManufacturingService.consume_components(mo, user=request.user)
            messages.success(request, 'Components consumed from stock.')
        except ValueError as e:
            messages.error(request, str(e))
        return redirect('mo-detail', pk=pk)


class MOProduceView(LoginRequiredMixinView, View):
    def post(self, request, pk):
        mo = get_object_or_404(ManufacturingOrder, pk=pk)
        form = ProduceForm(request.POST)
        
        if form.is_valid():
            try:
                qty = form.cleaned_data['quantity']
                ManufacturingService.produce(mo, qty, user=request.user)
                messages.success(request, f'{qty} units produced.')
            except ValueError as e:
                messages.error(request, str(e))
        else:
            messages.error(request, 'Invalid quantity.')
        
        return redirect('mo-detail', pk=pk)


class MOCompleteView(LoginRequiredMixinView, View):
    def post(self, request, pk):
        mo = get_object_or_404(ManufacturingOrder, pk=pk)
        try:
            ManufacturingService.complete_production(mo, user=request.user)
            messages.success(request, 'Production completed.')
        except ValueError as e:
            messages.error(request, str(e))
        return redirect('mo-detail', pk=pk)


class MOCancelView(LoginRequiredMixinView, View):
    def post(self, request, pk):
        mo = get_object_or_404(ManufacturingOrder, pk=pk)
        try:
            ManufacturingService.cancel_mo(mo)
            messages.success(request, 'Manufacturing Order cancelled.')
        except ValueError as e:
            messages.error(request, str(e))
        return redirect('mo-detail', pk=pk)

