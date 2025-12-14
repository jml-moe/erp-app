from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, View, DetailView, CreateView, UpdateView
from django.db.models import Q

from apps.employees.models import Employee, EmployeeSetting
from core.views import LoginRequiredMixinView
from .forms import PayrollForm
from .models import Payroll, PAYROLL_STATUS_CHOICES


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
    paginate_by = 20

    def get_queryset(self):
        user_settings, _ = EmployeeSetting.objects.get_or_create(actor=self.request.user)
        
        if user_settings.role == "manager":
            queryset = Payroll.objects.select_related("employee").all()
        else:
            # Regular users see only their own payrolls
            employee = Employee.objects.filter(actor=self.request.user).first()
            if employee:
                queryset = Payroll.objects.select_related("employee").filter(employee=employee)
            else:
                queryset = Payroll.objects.none()
        
        # Search functionality
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(employee__full_name__icontains=search) |
                Q(employee__employee_number__icontains=search)
            )
        
        # Filter by status
        status = self.request.GET.get('status', '')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by employee
        employee_id = self.request.GET.get('employee', '')
        if employee_id and user_settings.role == "manager":
            queryset = queryset.filter(employee_id=employee_id)
        
        return queryset.order_by("-month", "-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status', '')
        context['employee_filter'] = self.request.GET.get('employee', '')
        context['status_choices'] = PAYROLL_STATUS_CHOICES
        
        user_settings, _ = EmployeeSetting.objects.get_or_create(actor=self.request.user)
        if user_settings.role == "manager":
            context['employees'] = Employee.objects.filter(is_active=True).order_by('full_name')
        
        return context


class PayrollDetailView(LoginRequiredMixinView, BaseContextMixin, DetailView):
    model = Payroll
    template_name = "payrolls/payroll_detail.html"
    context_object_name = "payroll"

    def get_queryset(self):
        queryset = Payroll.objects.select_related("employee")
        user_settings, _ = EmployeeSetting.objects.get_or_create(actor=self.request.user)
        
        # Non-managers can only view their own payrolls
        if user_settings.role != "manager":
            employee = Employee.objects.filter(actor=self.request.user).first()
            if employee:
                queryset = queryset.filter(employee=employee)
            else:
                queryset = queryset.none()
        
        return queryset


class PayrollCreateView(ManagerRequiredMixin, BaseContextMixin, CreateView):
    model = Payroll
    form_class = PayrollForm
    template_name = "payrolls/payroll_form.html"
    success_url = reverse_lazy("payroll-list")

    def form_valid(self, form):
        form.instance.actor = self.request.user
        
        # Auto-fill gross_salary from employee if not set
        if form.instance.employee and form.instance.employee.salary:
            if not form.instance.gross_salary:
                form.instance.gross_salary = form.instance.employee.salary
        
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
        from django.utils import timezone
        from .models import Payroll
        
        user_settings, _ = EmployeeSetting.objects.get_or_create(actor=request.user)
        active_employees = Employee.objects.filter(is_active=True).count()
        
        # Get current month
        current_month = timezone.now().date().replace(day=1)
        
        # Count payrolls by status for current month
        pending_payrolls = Payroll.objects.filter(
            month=current_month,
            status__in=['draft', 'pending']
        ).count()
        
        processing_payrolls = Payroll.objects.filter(
            month=current_month,
            status='processing'
        ).count()
        
        paid_payrolls = Payroll.objects.filter(
            month=current_month,
            status='paid'
        ).count()
        
        # Check if we should process existing or create new
        process_existing = request.GET.get('process_existing', 'false').lower() == 'true'
        
        context = {
            "user_settings": user_settings,
            "active_employees": active_employees,
            "pending_payrolls": pending_payrolls,
            "processing_payrolls": processing_payrolls,
            "paid_payrolls": paid_payrolls,
            "current_month": current_month,
            "process_existing": process_existing,
        }
        return render(request, "payrolls/payroll_process.html", context)

    def post(self, request):
        from .methods import process_payrolls
        
        action = request.POST.get("action")
        process_existing = request.POST.get("process_existing", 'false').lower() == 'true'

        if action == "process":
            # Process synchronously for immediate feedback
            # You can change this back to async task if needed
            try:
                process_payrolls(process_existing=process_existing)
                messages.success(request, "Payrolls processed successfully!")
            except Exception as e:
                messages.error(request, f"Error processing payrolls: {str(e)}")
            
            # If you want async processing, uncomment below:
            # process_payrolls_task(process_existing=process_existing)

        return redirect("payroll-process")