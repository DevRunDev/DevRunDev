from django.urls import path

from .views import (
    CancelEnrollmentView,
    EnrollSuccessView,
    EnrollView,
    MarkLessonCompletedView,
    StudentDashboardView,
)

app_name = "enrollments"  # ✅ 네임스페이스 확인

urlpatterns = [
    path("enroll/<int:course_id>/", EnrollView.as_view(), name="enroll_course"),
    path("enroll/<int:course_id>/success/", EnrollSuccessView.as_view(), name="enroll_success"),
    path("lesson/<int:lesson_id>/complete/", MarkLessonCompletedView.as_view(), name="lesson_complete"),
    path("cancel/<int:course_id>/", CancelEnrollmentView.as_view(), name="cancel_enrollment"),
    path("dashboard/", StudentDashboardView.as_view(), name="student_dashboard"),
]
