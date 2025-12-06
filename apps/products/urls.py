from django.urls import path
from .views import (
    CategoryListView, CategoryCreateView, CategoryUpdateView, CategoryDeleteView,
    UnitOfMeasureListView, UnitOfMeasureCreateView, UnitOfMeasureUpdateView, UnitOfMeasureDeleteView,
    ProductListView, ProductDetailView, ProductCreateView, ProductUpdateView, ProductDeleteView,
    get_product_price,
)

urlpatterns = [
    # Categories
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/create/', CategoryCreateView.as_view(), name='category-create'),
    path('categories/<str:pk>/edit/', CategoryUpdateView.as_view(), name='category-update'),
    path('categories/<str:pk>/delete/', CategoryDeleteView.as_view(), name='category-delete'),
    
    # Units of Measure
    path('uom/', UnitOfMeasureListView.as_view(), name='uom-list'),
    path('uom/create/', UnitOfMeasureCreateView.as_view(), name='uom-create'),
    path('uom/<str:pk>/edit/', UnitOfMeasureUpdateView.as_view(), name='uom-update'),
    path('uom/<str:pk>/delete/', UnitOfMeasureDeleteView.as_view(), name='uom-delete'),
    
    # Products
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/create/', ProductCreateView.as_view(), name='product-create'),
    path('products/<str:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('products/<str:pk>/edit/', ProductUpdateView.as_view(), name='product-update'),
    path('products/<str:pk>/delete/', ProductDeleteView.as_view(), name='product-delete'),
    
    # API
    path('api/products/<str:product_id>/price/', get_product_price, name='product-price-api'),
]

