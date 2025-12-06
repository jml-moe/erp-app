from django.contrib import admin
from django.urls import path, include

from apps import announcements

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.announcements.urls")),
    path("", include("apps.employees.urls")),
    path("", include("apps.payrolls.urls")),
    path("", include("apps.authentications.urls")),
    path("", include("apps.products.urls")),
    path("", include("apps.vendors.urls")),
    path("", include("apps.inventory.urls")),
    path("", include("apps.purchasing.urls")),
    path("", include("apps.manufacturing.urls")),
    path("", include("apps.sales.urls")),
]
