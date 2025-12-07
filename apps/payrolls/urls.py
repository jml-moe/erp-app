from django.urls import path

from .views import (
    PayrollCreateView,
    PayrollDetailView,
    PayrollListView,
    PayrollProcessView,
    PayrollUpdateView,
)

urlpatterns = [
    path("payroll/", PayrollListView.as_view(), name="payroll-list"),
    path("payroll/create/", PayrollCreateView.as_view(), name="payroll-create"),
    path("payroll/process/", PayrollProcessView.as_view(), name="payroll-process"),
    path("payroll/<str:pk>/", PayrollDetailView.as_view(), name="payroll-detail"),
    path("payroll/<str:pk>/edit/", PayrollUpdateView.as_view(), name="payroll-update"),
]