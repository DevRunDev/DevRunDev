from django.contrib.auth import views
from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("profile/", views.ProfileView.as_view(template_name='account/profile.html'), name="profile"),
    path(
        "instructor/apply/",
        views.InstructorApplicationView.as_view(),
        name="instructor_apply",
    ),
    path("signup/", views.CustomSignupView.as_view(), name="signup"),
]
