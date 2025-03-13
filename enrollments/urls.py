from django.urls import path

from .views import EnrollRequiredView, EnrollSuccessView, EnrollView

app_name = "enrollments"  # ✅ 네임스페이스 추가

urlpatterns = [
    path("enroll/<int:course_id>/", EnrollView.as_view(), name="enroll_course"),
    path("enroll/<int:course_id>/success/", EnrollSuccessView.as_view(), name="enroll_success"),
    path(
        "enroll/<int:course_id>/required/", EnrollRequiredView.as_view(), name="enroll_required"
    ),  # ✅ 수강 제한 안내 페이지
]
