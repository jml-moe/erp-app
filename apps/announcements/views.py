from django.shortcuts import redirect
from django.views.generic import ListView, View
from apps.announcements.models import Announcement
from core.views import LoginRequiredMixinView
from apps.employees.models import EmployeeSetting

class AnnouncementListView(LoginRequiredMixinView, ListView):
    model = Announcement
    template_name = "announcement_list.html"
    context_object_name = "announcements"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_settings, created = EmployeeSetting.objects.get_or_create(actor=self.request.user)

        context["user_settings"] = user_settings
        return context

class DefaultView(View):
    def get(self, request, *args, **kwargs):
        return redirect('announcement-list')