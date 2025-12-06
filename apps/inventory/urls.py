from django.urls import path
from .views import (
    WarehouseListView, WarehouseCreateView, WarehouseUpdateView, WarehouseDeleteView,
    LocationListView, LocationCreateView, LocationUpdateView, LocationDeleteView,
    StockListView, StockMoveListView,
    StockPickingListView, StockPickingDetailView, StockPickingCreateView, StockPickingUpdateView,
    StockPickingValidateView, StockPickingLineCreateView,
    StockAdjustmentListView, StockAdjustmentCreateView, StockAdjustmentDetailView,
)

urlpatterns = [
    # Warehouses
    path('warehouses/', WarehouseListView.as_view(), name='warehouse-list'),
    path('warehouses/create/', WarehouseCreateView.as_view(), name='warehouse-create'),
    path('warehouses/<str:pk>/edit/', WarehouseUpdateView.as_view(), name='warehouse-update'),
    path('warehouses/<str:pk>/delete/', WarehouseDeleteView.as_view(), name='warehouse-delete'),
    
    # Locations
    path('locations/', LocationListView.as_view(), name='location-list'),
    path('locations/create/', LocationCreateView.as_view(), name='location-create'),
    path('locations/<str:pk>/edit/', LocationUpdateView.as_view(), name='location-update'),
    path('locations/<str:pk>/delete/', LocationDeleteView.as_view(), name='location-delete'),
    
    # Stock
    path('stock/', StockListView.as_view(), name='stock-list'),
    path('stock/moves/', StockMoveListView.as_view(), name='stock-move-list'),
    
    # Stock Pickings
    path('pickings/', StockPickingListView.as_view(), name='picking-list'),
    path('pickings/create/', StockPickingCreateView.as_view(), name='picking-create'),
    path('pickings/<str:pk>/', StockPickingDetailView.as_view(), name='picking-detail'),
    path('pickings/<str:pk>/edit/', StockPickingUpdateView.as_view(), name='picking-update'),
    path('pickings/<str:pk>/validate/', StockPickingValidateView.as_view(), name='picking-validate'),
    path('pickings/<str:picking_pk>/lines/create/', StockPickingLineCreateView.as_view(), name='picking-line-create'),
    
    # Stock Adjustments
    path('adjustments/', StockAdjustmentListView.as_view(), name='adjustment-list'),
    path('adjustments/create/', StockAdjustmentCreateView.as_view(), name='adjustment-create'),
    path('adjustments/<str:pk>/', StockAdjustmentDetailView.as_view(), name='adjustment-detail'),
]

