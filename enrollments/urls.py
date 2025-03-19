from django.urls import path

from .views import (
    AddToCartView,
    CartView,
    DownloadCertificateView,
    EnrollFromCartView,
    EnrollmentDetailView,
    EnrollmentListView,
    EnrollSuccessView,
    EnrollView,
    GenerateCertificateView,
    MarkLessonCompletedView,
    StudentDashboardView,
    ViewCertificateView,
)

app_name = "enrollments"

urlpatterns = [
    path("enroll/<int:course_id>/", EnrollView.as_view(), name="enroll_course"),
    path("enroll/<int:course_id>/success/", EnrollSuccessView.as_view(), name="enroll_success"),
    path("lesson/<int:lesson_id>/complete/", MarkLessonCompletedView.as_view(), name="lesson_complete"),
    path("dashboard/", StudentDashboardView.as_view(), name="student_dashboard"),
    path("", EnrollmentListView.as_view(), name="enrollment_list"),
    path("<int:pk>/", EnrollmentDetailView.as_view(), name="enrollment_detail"),
    path("<int:enrollment_id>/generate-certificate/", GenerateCertificateView.as_view(), name="generate_certificate"),
    path("certificate/<str:certificate_id>/", ViewCertificateView.as_view(), name="view_certificate"),
    path("certificate/<str:certificate_id>/download/", DownloadCertificateView.as_view(), name="download_certificate"),
    path("cart/", CartView.as_view(), name="cart"),
    path("cart/add/<int:course_id>/", AddToCartView.as_view(), name="add_to_cart"),
    path("cart/enroll/", EnrollFromCartView.as_view(), name="enroll_from_cart"),
]
