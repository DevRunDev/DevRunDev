from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("users/", include("accounts.urls")),
    path("courses/", include("courses.urls")),
]
