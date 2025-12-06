from django.db import models
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect

from core.views import LoginRequiredMixinView
from apps.employees.models import EmployeeSetting
from .models import Vendor, VendorContact, VendorProduct
from .forms import VendorForm, VendorContactForm, VendorProductForm


class BaseContextMixin:
    """Mixin to add common context data"""
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_settings, created = EmployeeSetting.objects.get_or_create(actor=self.request.user)
        context["user_settings"] = user_settings
        return context


# Vendor Views
class VendorListView(LoginRequiredMixinView, BaseContextMixin, ListView):
    model = Vendor
    template_name = "vendors/vendor_list.html"
    context_object_name = "vendors"
    
    def get_queryset(self):
        queryset = Vendor.objects.filter(is_active=True)
        
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(name__icontains=search) |
                models.Q(code__icontains=search) |
                models.Q(email__icontains=search)
            )
        
        # Filter by rating
        rating = self.request.GET.get('rating')
        if rating:
            queryset = queryset.filter(rating=rating)
        
        return queryset


class VendorDetailView(LoginRequiredMixinView, BaseContextMixin, DetailView):
    model = Vendor
    template_name = "vendors/vendor_detail.html"
    context_object_name = "vendor"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contacts'] = self.object.contacts.all()
        context['vendor_products'] = self.object.vendor_products.filter(is_active=True).select_related('product')
        return context


class VendorCreateView(LoginRequiredMixinView, BaseContextMixin, CreateView):
    model = Vendor
    form_class = VendorForm
    template_name = "vendors/vendor_form.html"
    success_url = reverse_lazy('vendor-list')
    
    def form_valid(self, form):
        form.instance.actor = self.request.user
        messages.success(self.request, 'Vendor created successfully.')
        return super().form_valid(form)


class VendorUpdateView(LoginRequiredMixinView, BaseContextMixin, UpdateView):
    model = Vendor
    form_class = VendorForm
    template_name = "vendors/vendor_form.html"
    
    def get_success_url(self):
        return reverse('vendor-detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Vendor updated successfully.')
        return super().form_valid(form)


class VendorDeleteView(LoginRequiredMixinView, BaseContextMixin, DeleteView):
    model = Vendor
    template_name = "vendors/vendor_confirm_delete.html"
    success_url = reverse_lazy('vendor-list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Vendor deleted successfully.')
        return super().delete(request, *args, **kwargs)


# VendorContact Views
class VendorContactCreateView(LoginRequiredMixinView, BaseContextMixin, CreateView):
    model = VendorContact
    form_class = VendorContactForm
    template_name = "vendors/vendor_contact_form.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vendor'] = get_object_or_404(Vendor, pk=self.kwargs['vendor_pk'])
        return context
    
    def form_valid(self, form):
        form.instance.vendor = get_object_or_404(Vendor, pk=self.kwargs['vendor_pk'])
        form.instance.actor = self.request.user
        messages.success(self.request, 'Contact added successfully.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('vendor-detail', kwargs={'pk': self.kwargs['vendor_pk']})


class VendorContactUpdateView(LoginRequiredMixinView, BaseContextMixin, UpdateView):
    model = VendorContact
    form_class = VendorContactForm
    template_name = "vendors/vendor_contact_form.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vendor'] = self.object.vendor
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Contact updated successfully.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('vendor-detail', kwargs={'pk': self.object.vendor.pk})


class VendorContactDeleteView(LoginRequiredMixinView, BaseContextMixin, DeleteView):
    model = VendorContact
    template_name = "vendors/vendor_contact_confirm_delete.html"
    
    def get_success_url(self):
        return reverse('vendor-detail', kwargs={'pk': self.object.vendor.pk})
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Contact deleted successfully.')
        return super().delete(request, *args, **kwargs)


# VendorProduct Views
class VendorProductCreateView(LoginRequiredMixinView, BaseContextMixin, CreateView):
    model = VendorProduct
    form_class = VendorProductForm
    template_name = "vendors/vendor_product_form.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vendor'] = get_object_or_404(Vendor, pk=self.kwargs['vendor_pk'])
        return context
    
    def form_valid(self, form):
        form.instance.vendor = get_object_or_404(Vendor, pk=self.kwargs['vendor_pk'])
        form.instance.actor = self.request.user
        messages.success(self.request, 'Product added to vendor successfully.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('vendor-detail', kwargs={'pk': self.kwargs['vendor_pk']})


class VendorProductUpdateView(LoginRequiredMixinView, BaseContextMixin, UpdateView):
    model = VendorProduct
    form_class = VendorProductForm
    template_name = "vendors/vendor_product_form.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vendor'] = self.object.vendor
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Vendor product updated successfully.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('vendor-detail', kwargs={'pk': self.object.vendor.pk})


class VendorProductDeleteView(LoginRequiredMixinView, BaseContextMixin, DeleteView):
    model = VendorProduct
    template_name = "vendors/vendor_product_confirm_delete.html"
    
    def get_success_url(self):
        return reverse('vendor-detail', kwargs={'pk': self.object.vendor.pk})
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Vendor product removed successfully.')
        return super().delete(request, *args, **kwargs)

