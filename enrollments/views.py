from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import TemplateView

from courses.models import Course

from .models import Enrollment


class EnrollView(LoginRequiredMixin, View):
    """✅ 모든 사용자(학생, 강사, 관리자) 수강 신청 가능"""

    def post(self, request, *args, **kwargs):
        course = get_object_or_404(Course, id=self.kwargs["course_id"])

        # 🚨 강사가 자신의 강의에 대해 수강 신청을 할 수 없도록 처리
        if request.user == course.instructor:
            messages.warning(request, "본인의 강의는 수강 신청할 필요가 없습니다.")
            return redirect("courses:course_detail", pk=course.id)  # ✅ 자신의 강의 상세 페이지로 리디렉션

        # 🚨 중복 수강 방지
        if Enrollment.objects.filter(student=request.user, course=course).exists():
            messages.warning(request, "이미 수강 중인 강의입니다.")
            return redirect("courses:course_detail", pk=course.id)  # ✅ pk 사용

        # ✅ 수강 신청 등록
        Enrollment.objects.create(student=request.user, course=course, status="approved")

        # ✅ 안내 메시지를 포함한 수강 신청 완료 페이지로 이동
        return redirect("enrollments:enroll_success", course.id)


class EnrollSuccessView(LoginRequiredMixin, View):
    """✅ 수강 신청 완료 안내 페이지"""

    def get(self, request, *args, **kwargs):
        course = get_object_or_404(Course, id=self.kwargs["course_id"])

        return render(request, "enrollments/enroll_success.html", {"course": course})


class EnrollRequiredView(TemplateView):
    """✅ 수강 신청 안내 페이지"""

    template_name = "enrollments/enroll_required.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["course"] = get_object_or_404(Course, id=self.kwargs["course_id"])
        return context
