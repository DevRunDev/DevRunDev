from django.urls import path

from .views import (
    CourseDetailView,
    CourseListView,
    CourseStep1View,
    CourseStep2View,
    CourseStep3View,
    CourseStep4View,
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
    # ✅ 강의 목록 조회
    path("", CourseListView.as_view(), name="course_list"),
    # ✅ 강의 상세 조회
    path("course/<int:pk>/", CourseDetailView.as_view(), name="course_detail"),
    # ✅ 레슨 상세 조회
    path("lesson/<int:pk>/", LessonDetailView.as_view(), name="lesson_detail"),
    # ✅ 강의 생성 (단계별)
    path("create/step1/", CourseStep1View.as_view(), name="course_step1"),
    path("create/step2/", CourseStep2View.as_view(), name="course_step2"),
    path("create/step3/", CourseStep3View.as_view(), name="course_step3"),
    path("create/step4/", CourseStep4View.as_view(), name="course_step4"),
    # ✅ 강사 대시보드 및 강의 수정
    path("instructor/dashboard/", InstructorDashboardView.as_view(), name="instructor_dashboard"),
    path("course/<int:pk>/edit/", CourseUpdateView.as_view(), name="course_edit"),
    # ✅ 섹션 관련 URL
    path("sections/<int:pk>/add/", SectionCreateView.as_view(), name="section_add"),
    path("sections/<int:pk>/edit/", SectionUpdateView.as_view(), name="section_edit"),
    path("sections/<int:pk>/delete/", SectionDeleteView.as_view(), name="section_delete"),
    # ✅ 레슨 관련 URL
    path("lessons/<int:pk>/add/", LessonCreateView.as_view(), name="lesson_add"),
    path("lessons/<int:pk>/edit/", LessonUpdateView.as_view(), name="lesson_edit"),
    path("lessons/<int:pk>/delete/", LessonDeleteView.as_view(), name="lesson_delete"),
]
