from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View
from django.views.generic import DetailView, ListView

from courses.models import Course, Lesson, Section

from .models import Certificate, Enrollment, LessonProgress


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


class StudentDashboardView(LoginRequiredMixin, View):
    """✅ 학생 대시보드 (진행 중인 강의, 완료된 강의, 이어보기 제공)"""

    def get(self, request, *args, **kwargs):
        enrollments = Enrollment.objects.filter(student=request.user)

        last_watched_lessons = []
        completed_enrollments = []

        for enrollment in enrollments:
            # ✅ 강의 진행률 업데이트 로직 추가
            enrollment.update_progress()

            # 수료증 확인
            try:
                certificate = enrollment.certificate
                enrollment.has_certificate = True
                enrollment.certificate_id = certificate.certificate_id
            except Certificate.DoesNotExist:
                enrollment.has_certificate = False
                enrollment.certificate_id = None

            # 수료 완료 여부 확인
            enrollment.is_completed = enrollment.is_course_completed()

            if enrollment.is_completed:
                completed_enrollments.append(enrollment)

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


class EnrollmentListView(LoginRequiredMixin, ListView):
    """학생의 수강 목록 조회"""

    model = Enrollment
    template_name = "enrollments/enrollment_list.html"
    context_object_name = "enrollments"

    def get_queryset(self):
        return Enrollment.objects.filter(student=self.request.user).select_related("course")


class EnrollmentDetailView(LoginRequiredMixin, DetailView):
    """수강 상세 정보 조회"""

    model = Enrollment
    template_name = "enrollments/enrollment_detail.html"
    context_object_name = "enrollment"

    def get_queryset(self):
        return Enrollment.objects.filter(student=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        enrollment = self.get_object()

        # 강의 진행 상황 확인
        context["is_completed"] = enrollment.is_course_completed()

        # 수료증 확인
        try:
            context["certificate"] = enrollment.certificate
        except Certificate.DoesNotExist:
            context["certificate"] = None

        return context


class GenerateCertificateView(LoginRequiredMixin, View):
    """수료증 생성 및 발급"""

    def get(self, request, enrollment_id):
        enrollment = get_object_or_404(Enrollment, id=enrollment_id, student=request.user)

        # 수료 조건 확인
        if not enrollment.is_course_completed():
            messages.error(request, "모든 강의와 퀴즈를 완료해야 수료증을 발급받을 수 있습니다.")
            return redirect("enrollments:enrollment_detail", pk=enrollment_id)

        # 수료증 생성 또는 조회
        certificate = enrollment.generate_certificate()

        if certificate:
            return redirect("enrollments:view_certificate", certificate_id=certificate.certificate_id)
        else:
            messages.error(request, "수료증 발급 중 오류가 발생했습니다.")
            return redirect("enrollments:enrollment_detail", pk=enrollment_id)


class ViewCertificateView(LoginRequiredMixin, DetailView):
    """수료증 조회"""

    model = Certificate
    template_name = "enrollments/certificate.html"
    context_object_name = "certificate"
    slug_field = "certificate_id"
    slug_url_kwarg = "certificate_id"

    def get_queryset(self):
        return Certificate.objects.filter(enrollment__student=self.request.user)


class DownloadCertificateView(LoginRequiredMixin, View):
    """수료증 PDF 다운로드(인쇄 페이지로 대체)"""

    def get(self, request, certificate_id):
        certificate = get_object_or_404(Certificate, certificate_id=certificate_id, enrollment__student=request.user)

        # 인쇄용 템플릿 사용
        return render(request, "enrollments/certificate_print.html", {"certificate": certificate, "print_mode": True})


class LessonCompleteView(LoginRequiredMixin, View):
    """레슨 완료 처리"""

    def post(self, request, lesson_id):
        lesson = get_object_or_404(Lesson, id=lesson_id)

        # 학생이 해당 강의를 수강 중인지 확인
        enrollment = get_object_or_404(Enrollment, student=request.user, course=lesson.section.course)

        # 레슨 진행 정보 생성 또는 업데이트
        lesson_progress, created = LessonProgress.objects.get_or_create(
            student=request.user, lesson=lesson, defaults={"completed": True}
        )

        if not created:
            lesson_progress.completed = True
            lesson_progress.save()

        # 전체 강의 진행률 업데이트
        enrollment.update_progress()

        return JsonResponse({"success": True})


class CartView(LoginRequiredMixin, ListView):
    """✅ 장바구니 보기 (로그인 필수)"""

    template_name = "enrollments/cart.html"
    context_object_name = "courses"
    login_url = "/accounts/login/"  # 로그인 페이지로 리디렉션

    def get_queryset(self):
        """세션에서 장바구니 가져오기"""
        cart = self.request.session.get("cart", [])
        return Course.objects.filter(id__in=cart)


class AddToCartView(LoginRequiredMixin, View):
    """✅ 장바구니에 강의 추가 (로그인 필수)"""

    login_url = "/accounts/login/"

    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)

        cart = request.session.get("cart", [])
        if str(course_id) not in cart:
            cart.append(str(course_id))
            request.session["cart"] = cart  # ✅ 세션 업데이트
            request.session.modified = True  # ✅ 장바구니 개수 즉시 반영
            messages.success(request, f'"{course.title}" 강의가 장바구니에 추가되었습니다.')
        else:
            messages.warning(request, "이미 장바구니에 있는 강의입니다.")

        return redirect("courses:course_list")


class EnrollFromCartView(LoginRequiredMixin, View):
    """✅ 장바구니에서 선택한 강의 수강 신청 (중복 방지)"""

    login_url = "/accounts/login/"

    def post(self, request):
        selected_courses = request.POST.getlist("selected_courses")  # ✅ 선택한 강의 가져오기
        if not selected_courses:
            messages.warning(request, "수강 신청할 강의를 선택해주세요.")
            return redirect("enrollments:cart")

        student = request.user
        enrolled_courses = []

        for course_id in selected_courses:
            course = Course.objects.get(id=course_id)
            enrollment, created = Enrollment.objects.get_or_create(student=student, course=course)

            if created:
                enrolled_courses.append(course_id)
                messages.success(request, f'"{course.title}" 강의가 수강 신청되었습니다.')
            else:
                messages.warning(request, f'"{course.title}" 강의는 이미 수강 신청한 상태입니다.')

        # ✅ 수강 신청한 강의만 장바구니에서 삭제
        cart = request.session.get("cart", [])
        request.session["cart"] = [str(course_id) for course_id in cart if str(course_id) not in selected_courses]
        request.session.modified = True  # ✅ 세션 변경 감지

        return redirect("enrollments:student_dashboard")
