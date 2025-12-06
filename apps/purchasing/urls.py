from django.urls import path
from .views import (
    RFQListView, RFQDetailView, RFQCreateView, RFQUpdateView,
    RFQLineCreateView, RFQLineUpdateView, RFQLineDeleteView,
    RFQSendView, RFQReceiveQuotationView, RFQConvertToPOView, RFQCancelView,
    POListView, PODetailView, POCreateView, POUpdateView,
    POLineCreateView, POLineDeleteView,
    POConfirmView, POSendView, POReceiveView, POMarkBilledView, POMarkDoneView, POCancelView,
)

urlpatterns = [
    # RFQ
    path('rfq/', RFQListView.as_view(), name='rfq-list'),
    path('rfq/create/', RFQCreateView.as_view(), name='rfq-create'),
    path('rfq/<str:pk>/', RFQDetailView.as_view(), name='rfq-detail'),
    path('rfq/<str:pk>/edit/', RFQUpdateView.as_view(), name='rfq-update'),
    path('rfq/<str:rfq_pk>/lines/create/', RFQLineCreateView.as_view(), name='rfq-line-create'),
    path('rfq-lines/<str:pk>/edit/', RFQLineUpdateView.as_view(), name='rfq-line-update'),
    path('rfq-lines/<str:pk>/delete/', RFQLineDeleteView.as_view(), name='rfq-line-delete'),
    
    # RFQ Actions
    path('rfq/<str:pk>/send/', RFQSendView.as_view(), name='rfq-send'),
    path('rfq/<str:pk>/receive-quotation/', RFQReceiveQuotationView.as_view(), name='rfq-receive-quotation'),
    path('rfq/<str:pk>/convert-to-po/', RFQConvertToPOView.as_view(), name='rfq-convert-to-po'),
    path('rfq/<str:pk>/cancel/', RFQCancelView.as_view(), name='rfq-cancel'),
    
    # Purchase Orders
    path('po/', POListView.as_view(), name='po-list'),
    path('po/create/', POCreateView.as_view(), name='po-create'),
    path('po/<str:pk>/', PODetailView.as_view(), name='po-detail'),
    path('po/<str:pk>/edit/', POUpdateView.as_view(), name='po-update'),
    path('po/<str:po_pk>/lines/create/', POLineCreateView.as_view(), name='po-line-create'),
    path('po-lines/<str:pk>/delete/', POLineDeleteView.as_view(), name='po-line-delete'),
    
    # PO Actions
    path('po/<str:pk>/confirm/', POConfirmView.as_view(), name='po-confirm'),
    path('po/<str:pk>/send/', POSendView.as_view(), name='po-send'),
    path('po/<str:pk>/receive/', POReceiveView.as_view(), name='po-receive'),
    path('po/<str:pk>/mark-billed/', POMarkBilledView.as_view(), name='po-mark-billed'),
    path('po/<str:pk>/mark-done/', POMarkDoneView.as_view(), name='po-mark-done'),
    path('po/<str:pk>/cancel/', POCancelView.as_view(), name='po-cancel'),
]

