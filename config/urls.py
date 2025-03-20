from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from courses.views import CourseListView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", CourseListView.as_view(), name="home"),
    path("accounts/", include("accounts.urls", namespace="accounts")),
    path("accounts/", include("allauth.urls")),
    path("courses/", include("courses.urls")),
    path("quizzes/", include("quizzes.urls")),
    path("enrollments/", include("enrollments.urls")),
    path("reviews/", include("reviews.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
