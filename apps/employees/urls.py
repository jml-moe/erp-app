from django.urls import path

from .views import (
    EmployeeCreateView,
    EmployeeDetailView,
    EmployeeListView,
    EmployeeUpdateView,
)

urlpatterns = [
    path("employees/", EmployeeListView.as_view(), name="employee-list"),
    path("employees/create/", EmployeeCreateView.as_view(), name="employee-create"),
    path("employees/<str:pk>/", EmployeeDetailView.as_view(), name="employee-detail"),
    path("employees/<str:pk>/edit/", EmployeeUpdateView.as_view(), name="employee-update"),
]