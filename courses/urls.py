from django.urls import path

from .views import (
    CourseDetailView,
    CourseListView,
    CourseStep1View,
    CourseStep2View,
    CourseStep3View,
    LessonDetailView,
)

app_name = "courses"

urlpatterns = [
    path("", CourseListView.as_view(), name="course_list"),
    path("<int:pk>/", CourseDetailView.as_view(), name="course_detail"),
    path("lesson/<int:pk>/", LessonDetailView.as_view(), name="lesson_detail"),
    path("create/step1/", CourseStep1View.as_view(), name="course_step1"),
    path("create/step2/", CourseStep2View.as_view(), name="course_step2"),
    path("create/step3/", CourseStep3View.as_view(), name="course_step3"),
]
