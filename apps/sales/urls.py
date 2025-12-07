from django.urls import path
from . import views

urlpatterns = [
    # Customer URLs
    path('customers/', views.CustomerListView.as_view(), name='customer-list'),
    path('customers/new/', views.CustomerCreateView.as_view(), name='customer-create'),
    path('customers/<str:pk>/', views.CustomerDetailView.as_view(), name='customer-detail'),
    path('customers/<str:pk>/edit/', views.CustomerUpdateView.as_view(), name='customer-update'),
    
    # Sales Quotation URLs
    path('quotations/', views.QuotationListView.as_view(), name='quotation-list'),
    path('quotations/new/', views.QuotationCreateView.as_view(), name='quotation-create'),
    path('quotations/<str:pk>/', views.QuotationDetailView.as_view(), name='quotation-detail'),
    path('quotations/<str:pk>/edit/', views.QuotationUpdateView.as_view(), name='quotation-update'),
    path('quotations/<str:quotation_pk>/lines/new/', views.QuotationLineCreateView.as_view(), name='quotation-line-create'),
    path('quotations/lines/<str:pk>/edit/', views.QuotationLineUpdateView.as_view(), name='quotation-line-update'),
    path('quotations/lines/<str:pk>/delete/', views.QuotationLineDeleteView.as_view(), name='quotation-line-delete'),
    path('quotations/<str:pk>/send/', views.QuotationSendView.as_view(), name='quotation-send'),
    path('quotations/<str:pk>/convert/', views.QuotationConvertToOrderView.as_view(), name='quotation-convert'),
    path('quotations/<str:pk>/cancel/', views.QuotationCancelView.as_view(), name='quotation-cancel'),
    
    # Sales Order URLs
    path('sales-orders/', views.SOListView.as_view(), name='so-list'),
    path('sales-orders/<str:pk>/', views.SODetailView.as_view(), name='so-detail'),
    path('sales-orders/<str:pk>/edit/', views.SOUpdateView.as_view(), name='so-update'),
    path('sales-orders/<str:so_pk>/lines/new/', views.SOLineCreateView.as_view(), name='so-line-create'),
    path('sales-orders/lines/<str:pk>/delete/', views.SOLineDeleteView.as_view(), name='so-line-delete'),
    path('sales-orders/<str:pk>/confirm/', views.SOConfirmView.as_view(), name='so-confirm'),
    path('sales-orders/<str:pk>/process/', views.SOProcessView.as_view(), name='so-process'),
    path('sales-orders/<str:pk>/ready/', views.SOReadyView.as_view(), name='so-ready'),
    path('sales-orders/<str:pk>/deliver/', views.SODeliverView.as_view(), name='so-deliver'),
    path('sales-orders/<str:pk>/complete/', views.SOCompleteView.as_view(), name='so-complete'),
    path('sales-orders/<str:pk>/cancel/', views.SOCancelView.as_view(), name='so-cancel'),
    path('sales-orders/<str:pk>/invoice/', views.SOCreateInvoiceView.as_view(), name='so-create-invoice'),
    
    # Sales Invoice URLs
    path('invoices/', views.InvoiceListView.as_view(), name='invoice-list'),
    path('invoices/new/', views.InvoiceCreateView.as_view(), name='invoice-create'),
    path('invoices/<str:pk>/', views.InvoiceDetailView.as_view(), name='invoice-detail'),
    path('invoices/<str:pk>/edit/', views.InvoiceUpdateView.as_view(), name='invoice-update'),
    path('invoices/<str:invoice_pk>/lines/new/', views.InvoiceLineCreateView.as_view(), name='invoice-line-create'),
    path('invoices/lines/<str:pk>/delete/', views.InvoiceLineDeleteView.as_view(), name='invoice-line-delete'),
    path('invoices/<str:pk>/send/', views.InvoiceSendView.as_view(), name='invoice-send'),
    path('invoices/<str:pk>/payment/', views.InvoicePaymentView.as_view(), name='invoice-payment'),
    path('invoices/<str:pk>/cancel/', views.InvoiceCancelView.as_view(), name='invoice-cancel'),
]

