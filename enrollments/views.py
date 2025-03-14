from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View

from courses.models import Course, Lesson, Section

from .models import Enrollment, LessonProgress


class EnrollView(LoginRequiredMixin, View):
    """✅ 모든 사용자(학생, 강사, 관리자) 수강 신청 가능"""

    def post(self, request, *args, **kwargs):
        course = get_object_or_404(Course, id=self.kwargs["course_id"])

        # ✅ 강사가 자신의 강의를 보는 경우 → 자동 접근 가능, 수강신청 불필요
        if request.user == course.instructor:
            messages.info(request, "본인의 강의는 수강 신청 없이 자동 접근 가능합니다.")
            return redirect("courses:course_detail", pk=course.id)

        # ✅ 이미 수강 중인지 확인
        if Enrollment.objects.filter(student=request.user, course=course).exists():
            messages.warning(request, "이미 수강 중인 강의입니다.")
            return redirect("courses:course_detail", pk=course.id)

        # ✅ 수강 신청 처리 (진행률 0%로 설정)
        Enrollment.objects.create(student=request.user, course=course, status="in_progress", progress=0)

        messages.success(request, f"'{course.title}' 수강 신청이 완료되었습니다.")
        return redirect("enrollments:enroll_success", course.id)


class EnrollSuccessView(LoginRequiredMixin, View):
    """✅ 수강 신청 완료 안내 페이지"""

    def get(self, request, *args, **kwargs):
        course = get_object_or_404(Course, id=self.kwargs["course_id"])
        return render(request, "enrollments/enroll_success.html", {"course": course})


class MarkLessonCompletedView(LoginRequiredMixin, View):
    """✅ 레슨 완료 처리 (진행률 업데이트 포함)"""

    def post(self, request, *args, **kwargs):
        lesson = get_object_or_404(Lesson, id=self.kwargs["lesson_id"])
        course = lesson.section.course
        enrollment = get_object_or_404(Enrollment, student=request.user, course=course)

        # ✅ 레슨 완료 처리
        lesson_progress, created = LessonProgress.objects.get_or_create(
            student=request.user, lesson=lesson, defaults={"completed": True, "completed_at": timezone.now()}
        )

        progress_updated = created or not lesson_progress.completed

        if progress_updated:
            lesson_progress.completed = True
            lesson_progress.completed_at = timezone.now()
            lesson_progress.save()

            enrollment.update_progress()

            # ✅ 강의가 완료되었는지 체크
            total_lessons = Lesson.objects.filter(section__course=course).count()
            completed_lessons = LessonProgress.objects.filter(
                student=request.user, lesson__section__course=course, completed=True
            ).count()

            if completed_lessons == total_lessons:
                enrollment.last_watched_lesson = None
                enrollment.status = "completed"
                messages.success(request, f"🎉 '{course.title}' 강의를 완료했습니다!")
            else:
                # ✅ `update_last_watched()`가 없으므로 직접 `LessonProgress`에서 처리
                lesson_progress.last_watched_at = timezone.now()
                lesson_progress.save()

            enrollment.save()

        return redirect("courses:lesson_detail", lesson.id)


class CancelEnrollmentView(LoginRequiredMixin, View):
    """✅ 수강 취소 기능 (진행률 초기화 및 학습 데이터 삭제)"""

    def post(self, request, *args, **kwargs):
        course = get_object_or_404(Course, id=self.kwargs["course_id"])
        enrollment = get_object_or_404(Enrollment, student=request.user, course=course)

        # ✅ 해당 강의의 LessonProgress 데이터 삭제 (수강 취소 시)
        LessonProgress.objects.filter(student=request.user, lesson__section__course=course).delete()

        enrollment.delete()
        messages.success(request, f"'{course.title}' 강의 수강을 취소했습니다.")
        return redirect("enrollments:student_dashboard")


class StudentDashboardView(LoginRequiredMixin, View):
    """✅ 학생 대시보드 (진행 중인 강의, 완료된 강의, 이어보기 제공)"""

    def get(self, request, *args, **kwargs):
        enrollments = Enrollment.objects.filter(student=request.user)

        last_watched_lessons = []

        for enrollment in enrollments:
            # ✅ 강의 진행률 업데이트 로직 추가
            enrollment.update_progress()

            # ✅ 다음 이어볼 레슨 찾기
            sections = Section.objects.filter(course=enrollment.course).order_by("order")
            completed_lessons = LessonProgress.objects.filter(
                student=request.user, lesson__section__course=enrollment.course, completed=True
            ).values_list("lesson_id", flat=True)

            next_lesson = None

            for section in sections:
                lessons = Lesson.objects.filter(section=section).order_by("order")
                for lesson in lessons:
                    if lesson.id not in completed_lessons:
                        next_lesson = lesson
                        break
                if next_lesson:
                    break

            enrollment.last_watched_lesson = next_lesson
            enrollment.save()

            if next_lesson:
                last_watched_lessons.append(enrollment)

        context = {
            "in_progress_courses": enrollments.filter(status="in_progress"),
            "completed_courses": enrollments.filter(status="completed"),
            "last_watched_lessons": last_watched_lessons,
        }
        return render(request, "enrollments/student_dashboard.html", context)
