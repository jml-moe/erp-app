from django.urls import path
from .views import (
    BOMListView, BOMDetailView, BOMCreateView, BOMUpdateView, BOMDeleteView,
    BOMLineCreateView, BOMLineUpdateView, BOMLineDeleteView,
    MOListView, MODetailView, MOCreateView, MOUpdateView,
    MOConfirmView, MOStartView, MOConsumeView, MOProduceView, MOCompleteView, MOCancelView,
)

urlpatterns = [
    # Bill of Materials
    path('bom/', BOMListView.as_view(), name='bom-list'),
    path('bom/create/', BOMCreateView.as_view(), name='bom-create'),
    path('bom/<str:pk>/', BOMDetailView.as_view(), name='bom-detail'),
    path('bom/<str:pk>/edit/', BOMUpdateView.as_view(), name='bom-update'),
    path('bom/<str:pk>/delete/', BOMDeleteView.as_view(), name='bom-delete'),
    
    # BOM Lines
    path('bom/<str:bom_pk>/lines/create/', BOMLineCreateView.as_view(), name='bom-line-create'),
    path('bom-lines/<str:pk>/edit/', BOMLineUpdateView.as_view(), name='bom-line-update'),
    path('bom-lines/<str:pk>/delete/', BOMLineDeleteView.as_view(), name='bom-line-delete'),
    
    # Manufacturing Orders
    path('manufacturing/', MOListView.as_view(), name='mo-list'),
    path('manufacturing/create/', MOCreateView.as_view(), name='mo-create'),
    path('manufacturing/<str:pk>/', MODetailView.as_view(), name='mo-detail'),
    path('manufacturing/<str:pk>/edit/', MOUpdateView.as_view(), name='mo-update'),
    
    # MO Actions
    path('manufacturing/<str:pk>/confirm/', MOConfirmView.as_view(), name='mo-confirm'),
    path('manufacturing/<str:pk>/start/', MOStartView.as_view(), name='mo-start'),
    path('manufacturing/<str:pk>/consume/', MOConsumeView.as_view(), name='mo-consume'),
    path('manufacturing/<str:pk>/produce/', MOProduceView.as_view(), name='mo-produce'),
    path('manufacturing/<str:pk>/complete/', MOCompleteView.as_view(), name='mo-complete'),
    path('manufacturing/<str:pk>/cancel/', MOCancelView.as_view(), name='mo-cancel'),
]

