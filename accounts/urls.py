from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path(
        "instructor/apply/", views.instructor_application_view, name="instructor_apply"
    ),
]
