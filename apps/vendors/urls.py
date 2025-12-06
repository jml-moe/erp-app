from django.urls import path
from .views import (
    VendorListView, VendorDetailView, VendorCreateView, VendorUpdateView, VendorDeleteView,
    VendorContactCreateView, VendorContactUpdateView, VendorContactDeleteView,
    VendorProductCreateView, VendorProductUpdateView, VendorProductDeleteView,
)

urlpatterns = [
    # Vendors
    path('vendors/', VendorListView.as_view(), name='vendor-list'),
    path('vendors/create/', VendorCreateView.as_view(), name='vendor-create'),
    path('vendors/<str:pk>/', VendorDetailView.as_view(), name='vendor-detail'),
    path('vendors/<str:pk>/edit/', VendorUpdateView.as_view(), name='vendor-update'),
    path('vendors/<str:pk>/delete/', VendorDeleteView.as_view(), name='vendor-delete'),
    
    # Vendor Contacts
    path('vendors/<str:vendor_pk>/contacts/create/', VendorContactCreateView.as_view(), name='vendor-contact-create'),
    path('vendor-contacts/<str:pk>/edit/', VendorContactUpdateView.as_view(), name='vendor-contact-update'),
    path('vendor-contacts/<str:pk>/delete/', VendorContactDeleteView.as_view(), name='vendor-contact-delete'),
    
    # Vendor Products
    path('vendors/<str:vendor_pk>/products/create/', VendorProductCreateView.as_view(), name='vendor-product-create'),
    path('vendor-products/<str:pk>/edit/', VendorProductUpdateView.as_view(), name='vendor-product-update'),
    path('vendor-products/<str:pk>/delete/', VendorProductDeleteView.as_view(), name='vendor-product-delete'),
]

