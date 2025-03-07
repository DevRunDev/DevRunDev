from django.urls import path

from .views import CourseCreateView, CourseDetailView, CourseListView

urlpatterns = [
    path("", CourseListView.as_view(), name="course_list"),
    path("<int:pk>/", CourseDetailView.as_view(), name="course_detail"),
    path("create/", CourseCreateView.as_view(), name="course_create"),
]
