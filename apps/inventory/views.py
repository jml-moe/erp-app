from django.db import models
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView, View
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse

from core.views import LoginRequiredMixinView
from apps.employees.models import EmployeeSetting
from .models import Warehouse, Location, StockQuant, StockMove, StockPicking, StockPickingLine, StockAdjustment
from .forms import WarehouseForm, LocationForm, StockPickingForm, StockPickingLineForm, StockAdjustmentForm
from .services import StockService


class BaseContextMixin:
    """Mixin to add common context data"""
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_settings, created = EmployeeSetting.objects.get_or_create(actor=self.request.user)
        context["user_settings"] = user_settings
        return context


# Warehouse Views
class WarehouseListView(LoginRequiredMixinView, BaseContextMixin, ListView):
    model = Warehouse
    template_name = "inventory/warehouse_list.html"
    context_object_name = "warehouses"
    
    def get_queryset(self):
        return Warehouse.objects.filter(is_active=True).prefetch_related('locations')


class WarehouseCreateView(LoginRequiredMixinView, BaseContextMixin, CreateView):
    model = Warehouse
    form_class = WarehouseForm
    template_name = "inventory/warehouse_form.html"
    success_url = reverse_lazy('warehouse-list')
    
    def form_valid(self, form):
        form.instance.actor = self.request.user
        response = super().form_valid(form)
        
        # Create default locations
        warehouse = self.object
        Location.objects.create(
            name='Stock',
            code='STOCK',
            warehouse=warehouse,
            location_type='internal',
            is_default=True,
            actor=self.request.user
        )
        Location.objects.create(
            name='Input',
            code='INPUT',
            warehouse=warehouse,
            location_type='internal',
            actor=self.request.user
        )
        Location.objects.create(
            name='Output',
            code='OUTPUT',
            warehouse=warehouse,
            location_type='internal',
            actor=self.request.user
        )
        
        messages.success(self.request, 'Warehouse created with default locations.')
        return response


class WarehouseUpdateView(LoginRequiredMixinView, BaseContextMixin, UpdateView):
    model = Warehouse
    form_class = WarehouseForm
    template_name = "inventory/warehouse_form.html"
    success_url = reverse_lazy('warehouse-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Warehouse updated successfully.')
        return super().form_valid(form)


class WarehouseDeleteView(LoginRequiredMixinView, BaseContextMixin, DeleteView):
    model = Warehouse
    template_name = "inventory/warehouse_confirm_delete.html"
    success_url = reverse_lazy('warehouse-list')


# Location Views
class LocationListView(LoginRequiredMixinView, BaseContextMixin, ListView):
    model = Location
    template_name = "inventory/location_list.html"
    context_object_name = "locations"
    
    def get_queryset(self):
        queryset = Location.objects.filter(is_active=True).select_related('warehouse', 'parent')
        
        warehouse_id = self.request.GET.get('warehouse')
        if warehouse_id:
            queryset = queryset.filter(warehouse_id=warehouse_id)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['warehouses'] = Warehouse.objects.filter(is_active=True)
        return context


class LocationCreateView(LoginRequiredMixinView, BaseContextMixin, CreateView):
    model = Location
    form_class = LocationForm
    template_name = "inventory/location_form.html"
    success_url = reverse_lazy('location-list')
    
    def form_valid(self, form):
        form.instance.actor = self.request.user
        messages.success(self.request, 'Location created successfully.')
        return super().form_valid(form)


class LocationUpdateView(LoginRequiredMixinView, BaseContextMixin, UpdateView):
    model = Location
    form_class = LocationForm
    template_name = "inventory/location_form.html"
    success_url = reverse_lazy('location-list')


class LocationDeleteView(LoginRequiredMixinView, BaseContextMixin, DeleteView):
    model = Location
    template_name = "inventory/location_confirm_delete.html"
    success_url = reverse_lazy('location-list')


# Stock Views
class StockListView(LoginRequiredMixinView, BaseContextMixin, ListView):
    template_name = "inventory/stock_list.html"
    context_object_name = "stock_items"
    
    def get_queryset(self):
        warehouse_id = self.request.GET.get('warehouse')
        warehouse = None
        if warehouse_id:
            warehouse = get_object_or_404(Warehouse, pk=warehouse_id)
        
        return StockService.get_all_stock_levels(warehouse=warehouse)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['warehouses'] = Warehouse.objects.filter(is_active=True)
        
        warehouse_id = self.request.GET.get('warehouse')
        warehouse = None
        if warehouse_id:
            warehouse = get_object_or_404(Warehouse, pk=warehouse_id)
            context['selected_warehouse'] = warehouse
        
        context['total_valuation'] = StockService.get_stock_valuation(warehouse=warehouse)
        context['low_stock_items'] = StockService.get_low_stock_products(warehouse=warehouse)
        return context


class StockMoveListView(LoginRequiredMixinView, BaseContextMixin, ListView):
    model = StockMove
    template_name = "inventory/stock_move_list.html"
    context_object_name = "moves"
    paginate_by = 50
    
    def get_queryset(self):
        queryset = StockMove.objects.select_related(
            'product', 'location_src', 'location_dest'
        ).order_by('-created_at')
        
        state = self.request.GET.get('state')
        if state:
            queryset = queryset.filter(state=state)
        
        move_type = self.request.GET.get('type')
        if move_type:
            queryset = queryset.filter(move_type=move_type)
        
        return queryset


# Stock Picking Views
class StockPickingListView(LoginRequiredMixinView, BaseContextMixin, ListView):
    model = StockPicking
    template_name = "inventory/picking_list.html"
    context_object_name = "pickings"
    
    def get_queryset(self):
        queryset = StockPicking.objects.select_related(
            'location_src', 'location_dest'
        ).prefetch_related('lines').order_by('-created_at')
        
        picking_type = self.request.GET.get('type')
        if picking_type:
            queryset = queryset.filter(picking_type=picking_type)
        
        state = self.request.GET.get('state')
        if state:
            queryset = queryset.filter(state=state)
        
        return queryset


class StockPickingDetailView(LoginRequiredMixinView, BaseContextMixin, DetailView):
    model = StockPicking
    template_name = "inventory/picking_detail.html"
    context_object_name = "picking"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lines'] = self.object.lines.select_related('product', 'product__uom')
        return context


class StockPickingCreateView(LoginRequiredMixinView, BaseContextMixin, CreateView):
    model = StockPicking
    form_class = StockPickingForm
    template_name = "inventory/picking_form.html"
    
    def form_valid(self, form):
        form.instance.actor = self.request.user
        messages.success(self.request, 'Stock picking created successfully.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('picking-detail', kwargs={'pk': self.object.pk})


class StockPickingUpdateView(LoginRequiredMixinView, BaseContextMixin, UpdateView):
    model = StockPicking
    form_class = StockPickingForm
    template_name = "inventory/picking_form.html"
    
    def get_success_url(self):
        return reverse('picking-detail', kwargs={'pk': self.object.pk})


class StockPickingValidateView(LoginRequiredMixinView, View):
    """Validate/process a stock picking"""
    
    def post(self, request, pk):
        picking = get_object_or_404(StockPicking, pk=pk)
        
        if picking.state != 'ready':
            messages.error(request, 'Picking must be in Ready state to validate.')
            return redirect('picking-detail', pk=pk)
        
        try:
            from django.utils import timezone
            from django.db import transaction
            
            with transaction.atomic():
                for line in picking.lines.all():
                    # Create and process stock move
                    move = StockMove.objects.create(
                        product=line.product,
                        location_src=line.source_location,
                        location_dest=line.destination_location,
                        quantity=line.quantity,
                        quantity_done=line.quantity,
                        origin=picking.reference,
                        state='done',
                        date_done=timezone.now(),
                        actor=request.user
                    )
                    line.stock_move = move
                    line.quantity_done = line.quantity
                    line.save()
                    
                    # Update stock
                    StockService.process_move(move)
                
                picking.state = 'done'
                picking.date_done = timezone.now()
                picking.save()
            
            messages.success(request, 'Stock picking validated successfully.')
        except Exception as e:
            messages.error(request, f'Error validating picking: {str(e)}')
        
        return redirect('picking-detail', pk=pk)


class StockPickingLineCreateView(LoginRequiredMixinView, BaseContextMixin, CreateView):
    model = StockPickingLine
    form_class = StockPickingLineForm
    template_name = "inventory/picking_line_form.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['picking'] = get_object_or_404(StockPicking, pk=self.kwargs['picking_pk'])
        return context
    
    def form_valid(self, form):
        form.instance.picking = get_object_or_404(StockPicking, pk=self.kwargs['picking_pk'])
        form.instance.actor = self.request.user
        messages.success(self.request, 'Line added successfully.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('picking-detail', kwargs={'pk': self.kwargs['picking_pk']})


# Stock Adjustment Views
class StockAdjustmentListView(LoginRequiredMixinView, BaseContextMixin, ListView):
    model = StockAdjustment
    template_name = "inventory/adjustment_list.html"
    context_object_name = "adjustments"
    
    def get_queryset(self):
        return StockAdjustment.objects.select_related('location').order_by('-created_at')


class StockAdjustmentCreateView(LoginRequiredMixinView, BaseContextMixin, CreateView):
    model = StockAdjustment
    form_class = StockAdjustmentForm
    template_name = "inventory/adjustment_form.html"
    
    def form_valid(self, form):
        form.instance.actor = self.request.user
        messages.success(self.request, 'Stock adjustment created.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('adjustment-detail', kwargs={'pk': self.object.pk})


class StockAdjustmentDetailView(LoginRequiredMixinView, BaseContextMixin, DetailView):
    model = StockAdjustment
    template_name = "inventory/adjustment_detail.html"
    context_object_name = "adjustment"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lines'] = self.object.lines.select_related('product', 'product__uom')
        return context

