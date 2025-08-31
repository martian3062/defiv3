# config/urls.py
from django.contrib import admin
from django.urls import path, include
from app_core import views   # ✅ this import fixes "views not defined"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.index, name="index"),   # ✅ home page
    path("", include("app_core.urls")),    # include your app routes
]
