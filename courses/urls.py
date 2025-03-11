from django.urls import path

from .views import (
    CourseDetailView,
    CourseListView,
    CourseStep1View,
    CourseStep2View,
    CourseStep3View,
    CourseUpdateView,
    InstructorDashboardView,
    LessonCreateView,
    LessonDeleteView,
    LessonDetailView,
    LessonUpdateView,
    SectionCreateView,
    SectionDeleteView,
    SectionUpdateView,
)

app_name = "courses"

urlpatterns = [
    # ✅ 강의 목록 및 상세보기
    path("", CourseListView.as_view(), name="course_list"),
    path("<int:pk>/", CourseDetailView.as_view(), name="course_detail"),
    path("lesson/<int:pk>/", LessonDetailView.as_view(), name="lesson_detail"),
    # ✅ 강의 생성 (단계별)
    path("create/step1/", CourseStep1View.as_view(), name="course_step1"),
    path("create/step2/", CourseStep2View.as_view(), name="course_step2"),
    path("create/step3/", CourseStep3View.as_view(), name="course_step3"),
    # ✅ 강사 대시보드 및 강의 수정
    path(
        "instructor/dashboard/",
        InstructorDashboardView.as_view(),
        name="instructor_dashboard",
    ),
    path("<int:pk>/edit/", CourseUpdateView.as_view(), name="course_edit"),
    # ✅ 섹션 관련 URL
    path(
        "<int:course_pk>/sections/add/", SectionCreateView.as_view(), name="section_add"
    ),  # ✅ 일관성을 위해 course_pk 추가
    path("sections/<int:pk>/edit/", SectionUpdateView.as_view(), name="section_edit"),
    path("sections/<int:pk>/delete/", SectionDeleteView.as_view(), name="section_delete"),
    # ✅ 레슨 관련 URL
    path(
        "<int:section_pk>/lessons/add/", LessonCreateView.as_view(), name="lesson_add"
    ),  # ✅ 일관성을 위해 section_pk 추가
    path("lessons/<int:pk>/edit/", LessonUpdateView.as_view(), name="lesson_edit"),
    path("lessons/<int:pk>/delete/", LessonDeleteView.as_view(), name="lesson_delete"),
]
