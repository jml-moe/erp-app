from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from core.views import LoginRequiredMixinView
from .forms import EmployeeForm
from .models import Employee, EmployeeSetting


class BaseContextMixin:
    """Inject common context like user settings."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_settings, _ = EmployeeSetting.objects.get_or_create(actor=self.request.user)
        context["user_settings"] = user_settings
        return context


class ManagerRequiredMixin(LoginRequiredMixinView):
    """Restrict access to manager role only."""

    def dispatch(self, request, *args, **kwargs):
        user_settings, _ = EmployeeSetting.objects.get_or_create(actor=request.user)
        if user_settings.role != "manager":
            raise PermissionDenied("Only managers can perform this action.")
        return super().dispatch(request, *args, **kwargs)


class EmployeeListView(LoginRequiredMixinView, BaseContextMixin, ListView):
    model = Employee
    template_name = "employees/employee_list.html"
    context_object_name = "employees"


class EmployeeDetailView(LoginRequiredMixinView, BaseContextMixin, DetailView):
    model = Employee
    template_name = "employees/employee_detail.html"
    context_object_name = "employee"


class EmployeeCreateView(ManagerRequiredMixin, BaseContextMixin, CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = "employees/employee_form.html"
    success_url = reverse_lazy("employee-list")


class EmployeeUpdateView(ManagerRequiredMixin, BaseContextMixin, UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = "employees/employee_form.html"
    success_url = reverse_lazy("employee-list")