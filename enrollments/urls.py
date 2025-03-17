from django.urls import path

from .views import (CancelEnrollmentView, DownloadCertificateView,
                    EnrollmentDetailView, EnrollmentListView,
                    EnrollSuccessView, EnrollView, GenerateCertificateView,
                    MarkLessonCompletedView, StudentDashboardView,
                    ViewCertificateView)

app_name = "enrollments"  # ✅ 네임스페이스 확인

urlpatterns = [
    path("enroll/<int:course_id>/", EnrollView.as_view(), name="enroll_course"),
    path("enroll/<int:course_id>/success/", EnrollSuccessView.as_view(), name="enroll_success"),
    path("lesson/<int:lesson_id>/complete/", MarkLessonCompletedView.as_view(), name="lesson_complete"),
    path("cancel/<int:course_id>/", CancelEnrollmentView.as_view(), name="cancel_enrollment"),
    path("dashboard/", StudentDashboardView.as_view(), name="student_dashboard"),
    path('', EnrollmentListView.as_view(), name='enrollment_list'),
    path('<int:pk>/', EnrollmentDetailView.as_view(), name='enrollment_detail'),
    path('<int:enrollment_id>/generate-certificate/', GenerateCertificateView.as_view(), name='generate_certificate'),
    path('certificate/<str:certificate_id>/', ViewCertificateView.as_view(), name='view_certificate'),
    path('certificate/<str:certificate_id>/download/', DownloadCertificateView.as_view(), name='download_certificate'),

]
