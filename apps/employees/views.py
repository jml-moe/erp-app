from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.db.models import Q

from core.views import LoginRequiredMixinView
from .forms import EmployeeForm
from .models import Employee, EmployeeSetting, DEPARTMENT_CHOICES, EMPLOYMENT_TYPE_CHOICES


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
    paginate_by = 20

    def get_queryset(self):
        queryset = Employee.objects.all().select_related('actor')
        
        # Search functionality
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(full_name__icontains=search) |
                Q(employee_number__icontains=search) |
                Q(job_title__icontains=search) |
                Q(email__icontains=search)
            )
        
        # Filter by department
        department = self.request.GET.get('department', '')
        if department:
            queryset = queryset.filter(department=department)
        
        # Filter by employment type
        employment_type = self.request.GET.get('employment_type', '')
        if employment_type:
            queryset = queryset.filter(employment_type=employment_type)
        
        # Filter by status
        status = self.request.GET.get('status', '')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['department_filter'] = self.request.GET.get('department', '')
        context['employment_type_filter'] = self.request.GET.get('employment_type', '')
        context['status_filter'] = self.request.GET.get('status', '')
        context['departments'] = DEPARTMENT_CHOICES
        context['employment_types'] = EMPLOYMENT_TYPE_CHOICES
        return context


class EmployeeDetailView(LoginRequiredMixinView, BaseContextMixin, DetailView):
    model = Employee
    template_name = "employees/employee_detail.html"
    context_object_name = "employee"

    def get_queryset(self):
        return Employee.objects.select_related('actor').prefetch_related('payrolls')


class EmployeeCreateView(ManagerRequiredMixin, BaseContextMixin, CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = "employees/employee_form.html"
    success_url = reverse_lazy("employee-list")

    def form_valid(self, form):
        # Actor is now optional and can be set via form
        # Only set actor if not already set in form
        if not form.instance.actor:
            # Leave it as None - employee can exist without linked account
            pass
        return super().form_valid(form)


class EmployeeUpdateView(ManagerRequiredMixin, BaseContextMixin, UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = "employees/employee_form.html"
    success_url = reverse_lazy("employee-list")