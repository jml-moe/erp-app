from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.shortcuts import redirect

from core.views import LoginRequiredMixinView
from apps.employees.models import EmployeeSetting
from .models import Category, UnitOfMeasure, Product
from .forms import CategoryForm, UnitOfMeasureForm, ProductForm


class BaseContextMixin:
    """Mixin to add common context data"""
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_settings, created = EmployeeSetting.objects.get_or_create(actor=self.request.user)
        context["user_settings"] = user_settings
        return context


# Category Views
class CategoryListView(LoginRequiredMixinView, BaseContextMixin, ListView):
    model = Category
    template_name = "products/category_list.html"
    context_object_name = "categories"


class CategoryCreateView(LoginRequiredMixinView, BaseContextMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "products/category_form.html"
    success_url = reverse_lazy('category-list')


class CategoryUpdateView(LoginRequiredMixinView, BaseContextMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "products/category_form.html"
    success_url = reverse_lazy('category-list')


class CategoryDeleteView(LoginRequiredMixinView, BaseContextMixin, DeleteView):
    model = Category
    success_url = reverse_lazy('category-list')


# Unit of Measure Views
class UnitOfMeasureListView(LoginRequiredMixinView, BaseContextMixin, ListView):
    model = UnitOfMeasure
    template_name = "products/uom_list.html"
    context_object_name = "uoms"


class UnitOfMeasureCreateView(LoginRequiredMixinView, BaseContextMixin, CreateView):
    model = UnitOfMeasure
    form_class = UnitOfMeasureForm
    template_name = "products/uom_form.html"
    success_url = reverse_lazy('uom-list')


class UnitOfMeasureUpdateView(LoginRequiredMixinView, BaseContextMixin, UpdateView):
    model = UnitOfMeasure
    form_class = UnitOfMeasureForm
    template_name = "products/uom_form.html"
    success_url = reverse_lazy('uom-list')


class UnitOfMeasureDeleteView(LoginRequiredMixinView, BaseContextMixin, DeleteView):
    model = UnitOfMeasure
    success_url = reverse_lazy('uom-list')


# Product Views
class ProductListView(LoginRequiredMixinView, BaseContextMixin, ListView):
    model = Product
    template_name = "products/product_list.html"
    context_object_name = "products"
    
    def get_queryset(self):
        queryset = Product.objects.select_related('category', 'uom').order_by('name')
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        return context


class ProductDetailView(LoginRequiredMixinView, BaseContextMixin, DetailView):
    model = Product
    template_name = "products/product_detail.html"
    context_object_name = "product"


class ProductCreateView(LoginRequiredMixinView, BaseContextMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = "products/product_form.html"
    
    def get_success_url(self):
        return reverse('product-detail', kwargs={'pk': self.object.pk})


class ProductUpdateView(LoginRequiredMixinView, BaseContextMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "products/product_form.html"
    
    def get_success_url(self):
        return reverse('product-detail', kwargs={'pk': self.object.pk})


class ProductDeleteView(LoginRequiredMixinView, BaseContextMixin, DeleteView):
    model = Product
    success_url = reverse_lazy('product-list')


# API Views
@require_http_methods(["GET"])
def get_product_price(request, product_id):
    """API endpoint to get product price"""
    try:
        product = Product.objects.get(pk=product_id)
        
        # Determine price type from request parameter
        price_type = request.GET.get('type', 'sales')  # 'sales' or 'purchase'
        
        if price_type == 'purchase':
            # For purchase, use standard_price (cost price)
            price = float(product.standard_price)
        else:
            # For sales, use list_price (selling price)
            price = float(product.list_price)
        
        return JsonResponse({
            'success': True,
            'price': price,
            'product_name': product.name,
            'uom': product.uom.symbol if product.uom else '',
        })
    except Product.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Product not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
