from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, View, DetailView, CreateView, UpdateView

from apps.employees.models import Employee, EmployeeSetting
from core.views import LoginRequiredMixinView
from .forms import PayrollForm
from .models import Payroll
from .tasks import process_payrolls_task


class BaseContextMixin:
    """Inject shared context like user settings."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_settings, _ = EmployeeSetting.objects.get_or_create(actor=self.request.user)
        context["user_settings"] = user_settings
        return context


class ManagerRequiredMixin(LoginRequiredMixinView):
    """Limit access to manager role."""

    def dispatch(self, request, *args, **kwargs):
        user_settings, _ = EmployeeSetting.objects.get_or_create(actor=request.user)
        if user_settings.role != "manager":
            raise PermissionDenied("Only managers can perform this action.")
        return super().dispatch(request, *args, **kwargs)


class PayrollListView(LoginRequiredMixinView, BaseContextMixin, ListView):
    model = Payroll
    template_name = "payrolls/payroll_list.html"
    context_object_name = "payrolls"

    def get_queryset(self):
        user_settings, _ = EmployeeSetting.objects.get_or_create(actor=self.request.user)
        if user_settings.role == "manager":
            return Payroll.objects.select_related("employee").order_by("-month", "-created_at")

        employee = Employee.objects.filter(actor=self.request.user).first()
        if employee:
            return Payroll.objects.select_related("employee").filter(employee=employee).order_by("-month")
        return Payroll.objects.none()


class PayrollDetailView(LoginRequiredMixinView, BaseContextMixin, DetailView):
    model = Payroll
    template_name = "payrolls/payroll_detail.html"
    context_object_name = "payroll"


class PayrollCreateView(ManagerRequiredMixin, BaseContextMixin, CreateView):
    model = Payroll
    form_class = PayrollForm
    template_name = "payrolls/payroll_form.html"
    success_url = reverse_lazy("payroll-list")

    def form_valid(self, form):
        form.instance.actor = self.request.user
        return super().form_valid(form)


class PayrollUpdateView(ManagerRequiredMixin, BaseContextMixin, UpdateView):
    model = Payroll
    form_class = PayrollForm
    template_name = "payrolls/payroll_form.html"
    success_url = reverse_lazy("payroll-list")

    def form_valid(self, form):
        form.instance.actor = self.request.user
        return super().form_valid(form)


class PayrollProcessView(ManagerRequiredMixin, BaseContextMixin, View):
    def get(self, request):
        user_settings, _ = EmployeeSetting.objects.get_or_create(actor=request.user)
        return render(request, "payrolls/payroll_process.html", {"user_settings": user_settings})

    def post(self, request):
        action = request.POST.get("action")

        if action == "process":
            process_payrolls_task()

        return redirect("payroll-process")