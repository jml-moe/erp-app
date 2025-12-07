from django.shortcuts import redirect
from django.views.generic import ListView, View
from django.db.models import Sum, Count, Q
from apps.announcements.models import Announcement
from core.views import LoginRequiredMixinView
from apps.employees.models import EmployeeSetting
from apps.sales.models import SalesOrder, SalesInvoice
from apps.manufacturing.models import ManufacturingOrder
from apps.inventory.services import StockService
from apps.payrolls.models import Payroll

class AnnouncementListView(LoginRequiredMixinView, ListView):
    model = Announcement
    template_name = "announcement_list.html"
    context_object_name = "announcements"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_settings, _ = EmployeeSetting.objects.get_or_create(actor=self.request.user)

        context["user_settings"] = user_settings

        # Dashboard Summary Data
        # Sales Summary
        context['total_sales_orders'] = SalesOrder.objects.count()
        context['pending_sales_orders'] = SalesOrder.objects.filter(
            Q(state='draft') | Q(state='confirmed')
        ).count()
        context['total_sales_amount'] = SalesOrder.objects.filter(
            state='done'
        ).aggregate(total=Sum('total_amount'))['total'] or 0

        # Manufacturing Summary
        context['total_mo'] = ManufacturingOrder.objects.count()
        context['in_progress_mo'] = ManufacturingOrder.objects.filter(
            state='in_progress'
        ).count()

        # Inventory Summary
        try:
            context['low_stock_count'] = len(StockService.get_low_stock_products())
        except:
            context['low_stock_count'] = 0

        # Invoice Summary
        context['pending_invoices'] = SalesInvoice.objects.filter(
            state__in=['draft', 'sent']
        ).count()
        context['overdue_invoices'] = SalesInvoice.objects.filter(
            state='overdue'
        ).count()

        # Payroll Summary
        context['pending_payrolls'] = Payroll.objects.filter(
            status='pending'
        ).count()

        # Recent Sales Orders
        context['recent_sales_orders'] = SalesOrder.objects.select_related(
            'customer'
        ).order_by('-created_at')[:5]

        # Recent Manufacturing Orders
        context['recent_mo'] = ManufacturingOrder.objects.select_related(
            'product'
        ).order_by('-created_at')[:5]

        return context

class DefaultView(View):
    def get(self, request, *args, **kwargs):
        return redirect('announcement-list')