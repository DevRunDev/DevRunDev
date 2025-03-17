from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, ListView, UpdateView

from enrollments.models import Enrollment, LessonProgress
from quizzes.forms import QuizForm
from quizzes.models import Quiz
from reviews.models import Review

from .forms import CourseForm, LessonForm, SectionForm
from .models import Course, Lesson, Section


class CourseListView(ListView):
    model = Course
    template_name = "courses/course_list.html"
    context_object_name = "courses"
    ordering = ["-created_at"]

    def get_queryset(self):
        """✅ 승인된 강의만 조회하고, 평균 별점 계산"""
        queryset = Course.objects.filter(status="approved").annotate(avg_rating=Avg("reviews__rating"))
        search_query = self.request.GET.get("q")
        if search_query:
            queryset = queryset.filter(title__icontains=search_query)
        return queryset


class CourseDetailView(DetailView):
    model = Course
    template_name = "courses/course_detail.html"
    context_object_name = "course"

    def get_queryset(self):
        """✅ 모든 사용자가 승인된 강의에 접근할 수 있도록 설정"""
        queryset = Course.objects.filter(status="approved")
        if self.request.user.is_authenticated and self.request.user.is_instructor():
            queryset = Course.objects.all()  # ✅ 강사는 모든 강의 조회 가능
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()

        # ✅ 강의에 속한 섹션과 레슨 가져오기
        sections = Section.objects.filter(course=course).order_by("order")
        for section in sections:
            section.lessons_detail = Lesson.objects.filter(section=section).order_by("order")
        context["sections"] = sections

        # ✅ 기본 설정
        context["is_enrolled"] = False
        context["progress"] = 0  # ✅ 기본값을 0으로 설정
        context["completed_lessons"] = set()  # ✅ 완료된 레슨 목록을 저장할 Set
        context["average_rating"] = (
            course.reviews.aggregate(avg_rating=Avg("rating"))["avg_rating"] or 0
        )  # ✅ 평균 별점 추가

        if self.request.user.is_authenticated:
            # ✅ 강사는 항상 수강 상태를 True로 설정 (수강 신청 없이 레슨 접근 가능)
            if self.request.user == course.instructor:
                context["is_enrolled"] = True
            else:
                # ✅ 학생이 수강 중인지 확인
                enrollment = Enrollment.objects.filter(student=self.request.user, course=course).first()
                if enrollment:
                    context["is_enrolled"] = True
                    context["progress"] = enrollment.progress  # ✅ 진행률 반영

                    # ✅ 사용자가 완료한 레슨 목록을 가져와 저장
                    completed_lessons = LessonProgress.objects.filter(
                        student=self.request.user, completed=True
                    ).values_list("lesson_id", flat=True)
                    context["completed_lessons"] = set(completed_lessons)  # ✅ Set으로 변환하여 빠른 조회 가능

        # ✅ 학생이 이미 리뷰를 남겼는지 확인
        context["has_reviewed"] = False  # 기본값 설정
        if self.request.user.is_authenticated and not self.request.user.is_instructor():
            context["has_reviewed"] = Review.objects.filter(course=course, user=self.request.user).exists()

        return context


class LessonDetailView(LoginRequiredMixin, DetailView):
    model = Lesson
    template_name = "courses/lesson_detail.html"
    context_object_name = "lesson"

    def dispatch(self, request, *args, **kwargs):
        """🚨 수강하지 않은 사용자는 레슨 상세 페이지 접근 불가 (단, 강사는 예외)"""
        lesson = self.get_object()
        course = lesson.section.course

        # ✅ 강사는 항상 접근 가능, 학생은 수강 여부 확인 후 접근
        if (
            request.user != course.instructor
            and not Enrollment.objects.filter(student=request.user, course=course).exists()
        ):
            messages.warning(request, "이 강의의 레슨을 보려면 먼저 수강 신청을 해야 합니다.")
            return redirect("enrollments:enroll_course", course_id=course.id)

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """✅ 이전 레슨 및 다음 레슨 찾기 + 완료된 레슨 목록 추가"""
        context = super().get_context_data(**kwargs)
        lesson = self.get_object()
        section = lesson.section
        course = section.course

        # ✅ 완료된 레슨 목록 가져오기
        completed_lessons = LessonProgress.objects.filter(student=self.request.user, completed=True).values_list(
            "lesson_id", flat=True
        )
        context["completed_lessons"] = set(completed_lessons)  # ✅ 빠른 조회를 위해 Set 사용

        # ✅ 다음 레슨 찾기 (현재 섹션 내)
        next_lesson = (
            Lesson.objects.filter(section=section, order__gt=lesson.order).order_by("order").first()
            or Lesson.objects.filter(section__course=course, section__order__gt=section.order)
            .order_by("section__order", "order")
            .first()
        )

        # ✅ 이전 레슨 찾기 (현재 섹션 내)
        previous_lesson = (
            Lesson.objects.filter(section=section, order__lt=lesson.order).order_by("-order").first()
            or Lesson.objects.filter(section__course=course, section__order__lt=section.order)
            .order_by("-section__order", "-order")
            .first()
        )

        context["next_lesson"] = next_lesson
        context["previous_lesson"] = previous_lesson
        return context


class CourseStep1View(LoginRequiredMixin, View):
    """강의 기본 정보 입력 (1단계)"""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_instructor():
            messages.error(request, "강의 생성은 강사만 가능합니다. 강사 계정으로 로그인해주세요.")
            return redirect("courses:course_list")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = CourseForm()
        return render(request, "courses/course_step1.html", {"form": form})

    def post(self, request):
        form = CourseForm(request.POST)
        if form.is_valid():
            request.session["course_data"] = form.cleaned_data
            return redirect("courses:course_step2")
        return render(request, "courses/course_step1.html", {"form": form})


class CourseStep2View(LoginRequiredMixin, View):
    """섹션 정보 입력 (2단계)"""

    def dispatch(self, request, *args, **kwargs):
        if "course_data" not in request.session:
            return redirect("courses:course_step1")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = SectionForm()
        sections = request.session.get("section_data", [])  # ✅ 세션에서 섹션 데이터 유지
        return render(request, "courses/course_step2.html", {"form": form, "sections": sections})

    def post(self, request):
        if "add_section" in request.POST:
            # ✅ 섹션 추가 기능
            section_title = request.POST.get("section_title")
            if section_title:
                if "section_data" not in request.session:
                    request.session["section_data"] = []
                request.session["section_data"].append({"title": section_title})
                request.session.modified = True  # ✅ 세션 변경 저장
                messages.success(request, "새 섹션이 추가되었습니다.")
            return redirect("courses:course_step2")

        if "delete_section" in request.POST:
            # ✅ 섹션 삭제 기능 (세션 데이터 변경)
            section_title = request.POST.get("delete_section")
            if "section_data" in request.session and section_title:
                request.session["section_data"] = [
                    sec for sec in request.session["section_data"] if sec["title"] != section_title
                ]
                request.session.modified = True  # ✅ 세션 변경 저장
                messages.success(request, "섹션이 삭제되었습니다.")
            return redirect("courses:course_step2")

        # ✅ 다음 단계로 이동
        return redirect("courses:course_step3")


class CourseStep3View(LoginRequiredMixin, View):
    """레슨 정보 입력 및 강의 저장 (3단계)"""

    def dispatch(self, request, *args, **kwargs):
        if "course_data" not in request.session or "section_data" not in request.session:
            return redirect("courses:course_step1")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = LessonForm()

        # ✅ sections를 리스트로 변환하여 템플릿에서 쉽게 사용 가능하도록 변경
        sections_with_titles = [
            {"id": str(i), "title": sec["title"]} for i, sec in enumerate(request.session.get("section_data", []))
        ]

        # ✅ lessons_by_section을 리스트 형태로 변환하여 템플릿에서 쉽게 접근 가능하도록 변경
        lessons_by_section = [
            {
                "section_id": section["id"],
                "lessons": request.session.get("lesson_data", {}).get(section["id"], []),
            }
            for section in sections_with_titles
        ]

        return render(
            request,
            "courses/course_step3.html",
            {
                "form": form,
                "sections_with_titles": sections_with_titles,  # ✅ 리스트로 변환하여 템플릿에서 쉽게 접근 가능
                "lessons_by_section": lessons_by_section,  # ✅ 섹션별 레슨 리스트 변환
            },
        )

    def post(self, request):
        # ✅ sections 리스트를 다시 정의하여 post()에서도 접근 가능하도록 수정
        sections_with_titles = [
            {"id": str(i), "title": sec["title"]} for i, sec in enumerate(request.session.get("section_data", []))
        ]

        if "add_lesson" in request.POST:
            section_id = request.POST.get("section_id")
            lesson_title = request.POST.get("lesson_title")
            lesson_video_url = request.POST.get("lesson_video_url")

            if section_id and lesson_title and lesson_video_url:
                section_id = str(section_id)  # ✅ 문자열로 변환하여 일관성 유지

                if "lesson_data" not in request.session:
                    request.session["lesson_data"] = {}

                if section_id not in request.session["lesson_data"]:
                    request.session["lesson_data"][section_id] = []

                request.session["lesson_data"][section_id].append(
                    {"title": lesson_title, "video_url": lesson_video_url}
                )
                request.session.modified = True
                messages.success(
                    request,
                    f"새 레슨이 섹션 '{next((s['title'] for s in sections_with_titles if s['id'] == section_id), '알 수 없는 섹션')}'에 추가되었습니다.",
                )
            return redirect("courses:course_step3")

        if "delete_lesson" in request.POST:
            section_id = request.POST.get("section_id")
            lesson_title = request.POST.get("delete_lesson")

            if "lesson_data" in request.session and str(section_id) in request.session["lesson_data"]:
                request.session["lesson_data"][str(section_id)] = [
                    les for les in request.session["lesson_data"][str(section_id)] if les["title"] != lesson_title
                ]
                request.session.modified = True
                messages.success(
                    request,
                    f"레슨 '{lesson_title}'이 섹션 '{next((s['title'] for s in sections_with_titles if s['id'] == section_id), '알 수 없는 섹션')}'에서 삭제되었습니다.",
                )
            return redirect("courses:course_step3")

        lesson_data = request.session.get("lesson_data", {})
        if not any(lesson_data.values()):
            messages.warning(request, "최소한 하나의 레슨을 추가해야 합니다.")
            return redirect("courses:course_step3")

        course_data = request.session["course_data"]
        section_data = request.session["section_data"]

        course = Course.objects.create(
            instructor=request.user,
            title=course_data["title"],
            description=course_data["description"],
            price=course_data["price"],
            status="review",
        )

        section_id_map = {}
        for index, section in enumerate(section_data):
            sec = Section.objects.create(course=course, title=section["title"])
            section_id_map[str(index)] = sec.id

        for section_index, lessons in lesson_data.items():
            actual_section_id = section_id_map.get(section_index)
            if actual_section_id:
                for lesson in lessons:
                    Lesson.objects.create(
                        section=Section.objects.get(id=actual_section_id),
                        title=lesson["title"],
                        video_url=lesson["video_url"],
                    )

        del request.session["course_data"]
        del request.session["section_data"]
        if "lesson_data" in request.session:
            del request.session["lesson_data"]

        # 생성된 강의 ID를 세션에 저장 (CourseStep4View에서 사용)
        request.session["created_course_id"] = course.id
        request.session.modified = True

        messages.success(request, "강의 기본 정보가 저장되었습니다. 퀴즈를 추가해 강의를 완성하세요.")
        return redirect("courses:course_step4")  # 퀴즈 생성 페이지로 이동


class CourseStep4View(LoginRequiredMixin, View):
    """퀴즈 정보 입력 및 저장 (4단계)"""

    def dispatch(self, request, *args, **kwargs):
        # 로그인 및 강사 권한 확인
        if not request.user.is_authenticated or not request.user.is_instructor():
            messages.error(request, "강의 생성은 강사만 가능합니다. 강사 계정으로 로그인해주세요.")
            return redirect("courses:course_list")

        # 신규 생성된 강의 ID가 세션에 있는지 확인
        if "created_course_id" not in request.session:
            messages.error(request, "잘못된 접근입니다. 강의 생성부터 시작해주세요.")
            return redirect("courses:course_step1")

        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        # 세션에서 생성된 강의 ID 가져오기
        course_id = request.session.get("created_course_id")
        course = get_object_or_404(Course, id=course_id, instructor=request.user)

        # 강의의 모든 섹션과 레슨 가져오기
        sections = Section.objects.filter(course=course).order_by("order")

        # 각 섹션에 레슨 리스트 추가
        for section in sections:
            section.lessons_list = Lesson.objects.filter(section=section).order_by("order")

            # 각 레슨에 이미 생성된 퀴즈가 있는지 확인
            for lesson in section.lessons_list:
                lesson.quiz = Quiz.objects.filter(lesson=lesson).first()

        # 퀴즈 폼 초기화
        form = QuizForm(course=course)

        context = {
            "course": course,
            "sections": sections,
            "form": form,
        }

        return render(request, "courses/course_step4.html", context)

    def post(self, request):
        # 세션에서 생성된 강의 ID 가져오기
        course_id = request.session.get("created_course_id")
        course = get_object_or_404(Course, id=course_id, instructor=request.user)

        # 생성 또는 삭제 요청 처리
        if "create_quiz" in request.POST:
            # 퀴즈 생성 처리
            lesson_id = request.POST.get("lesson_id")
            lesson = get_object_or_404(Lesson, id=lesson_id)
            section = lesson.section

            # 퀴즈 정보 가져오기
            title = request.POST.get("title")
            description = request.POST.get("description", "")

            # 이미 퀴즈가 있는지 확인
            existing_quiz = Quiz.objects.filter(lesson=lesson).first()
            if existing_quiz:
                # 기존 퀴즈 업데이트
                existing_quiz.title = title
                existing_quiz.description = description
                existing_quiz.save()
                messages.success(request, f"레슨 '{lesson.title}'의 퀴즈가 업데이트되었습니다.")
            else:
                # 새 퀴즈 생성
                quiz = Quiz.objects.create(
                    title=title,
                    description=description,
                    course=course,
                    section=section,
                    lesson=lesson,
                    instructor=request.user,
                )
                messages.success(request, f"레슨 '{lesson.title}'에 새 퀴즈가 추가되었습니다.")

            return redirect("courses:course_step4")

        elif "delete_quiz" in request.POST:
            # 퀴즈 삭제 처리
            quiz_id = request.POST.get("quiz_id")
            quiz = get_object_or_404(Quiz, id=quiz_id, instructor=request.user)
            lesson_title = quiz.lesson.title
            quiz.delete()
            messages.success(request, f"레슨 '{lesson_title}'의 퀴즈가 삭제되었습니다.")
            return redirect("courses:course_step4")

        elif "finish" in request.POST:
            # 강의 생성 완료 처리
            # 세션에서 강의 ID 삭제
            del request.session["created_course_id"]
            messages.success(request, "강의 생성이 완료되었습니다!")
            return redirect("courses:course_detail", pk=course.id)

        # 기본적으로 같은 페이지로 리다이렉트
        return redirect("courses:course_step4")


class InstructorDashboardView(LoginRequiredMixin, View):
    """✅ 강사 대시보드 (내가 만든 강의 + 내가 수강한 강의)"""

    def get(self, request):
        if not request.user.is_instructor():
            messages.error(request, "강사만 접근할 수 있는 페이지입니다.")
            return redirect("courses:course_list")

        status_filter = request.GET.get("status")
        my_courses = Course.objects.filter(instructor=request.user)

        # ✅ 강사가 수강한 강의 목록 (본인이 만든 강의 제외)
        enrolled_courses = Enrollment.objects.filter(student=request.user).exclude(course__instructor=request.user)

        if status_filter in ["approved", "review", "not_approved"]:
            my_courses = my_courses.filter(status=status_filter)

        # ✅ 상태별 강의 개수 조회 (쿼리 최적화)
        course_counts = Course.objects.filter(instructor=request.user).values("status").annotate(count=Count("status"))
        status_counts = {item["status"]: item["count"] for item in course_counts}

        context = {
            "my_courses": my_courses,
            "enrolled_courses": enrolled_courses,
            "total_courses": sum(status_counts.values()),
            "approved_courses": status_counts.get("approved", 0),
            "review_courses": status_counts.get("review", 0),
            "rejected_courses": status_counts.get("not_approved", 0),
        }
        return render(request, "courses/instructor_dashboard.html", context)


class CourseUpdateView(LoginRequiredMixin, UpdateView):
    """강의 수정 뷰"""

    model = Course
    template_name = "courses/course_edit.html"
    form_class = CourseForm
    success_url = reverse_lazy("courses:instructor_dashboard")

    def dispatch(self, request, *args, **kwargs):
        """강사만 수정 가능하도록 제한"""
        course = self.get_object()

        # ✅ 강사가 아닌 경우 접근 제한
        if request.user.role.lower() != "instructor":
            messages.error(request, "강사만 강의를 수정할 수 있습니다.")
            return redirect("courses:course_list")  # ✅ 일반 사용자는 강의 목록으로 리디렉션

        # ✅ 강의 작성자가 아닌 경우 접근 제한
        if course.instructor != request.user:
            messages.error(request, "본인의 강의만 수정할 수 있습니다.")
            return redirect("courses:instructor_dashboard")

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """반려된 강의는 '심사 중' 상태로 변경하고, 승인된 강의는 상태 유지"""
        course = form.save(commit=False)
        if course.status == "not_approved":
            course.status = "review"
        course.save()

        section_titles = self.request.POST.getlist("section_titles")
        lesson_titles = self.request.POST.getlist("lesson_titles")
        lesson_video_urls = self.request.POST.getlist("lesson_video_urls")

        for section_title in section_titles:
            section, created = Section.objects.get_or_create(course=course, title=section_title)
            for lesson_title, lesson_video in zip(lesson_titles, lesson_video_urls):
                Lesson.objects.get_or_create(section=section, title=lesson_title, video_url=lesson_video)

        messages.success(self.request, "강의 수정이 완료되었습니다.")
        return super().form_valid(form)


class SectionCreateView(View):
    """새로운 섹션 추가"""

    def post(self, request, pk):
        course = Course.objects.get(pk=pk)
        title = request.POST.get("section_title")
        if title:
            Section.objects.create(course=course, title=title)
            messages.success(request, "새 섹션이 추가되었습니다.")
        return redirect("courses:course_edit", pk=pk)


class SectionUpdateView(LoginRequiredMixin, UpdateView):
    """섹션 수정 뷰"""

    model = Section
    template_name = "courses/section_edit.html"
    form_class = SectionForm

    def get_success_url(self):
        return reverse_lazy("courses:course_edit", kwargs={"pk": self.object.course.id})


class SectionDeleteView(View):
    """섹션 삭제"""

    def get(self, request, pk):
        section = Section.objects.get(pk=pk)
        course_id = section.course.id
        section.delete()
        messages.success(request, "섹션이 삭제되었습니다.")
        return redirect("courses:course_edit", pk=course_id)


class LessonCreateView(View):
    """새로운 레슨 추가"""

    def post(self, request, pk):
        section_id = request.POST.get("section_id")
        title = request.POST.get("lesson_title")
        video_url = request.POST.get("lesson_video_url")
        section = Section.objects.get(pk=section_id)
        Lesson.objects.create(section=section, title=title, video_url=video_url)
        messages.success(request, "새 레슨이 추가되었습니다.")
        return redirect("courses:course_edit", pk=pk)


class LessonUpdateView(LoginRequiredMixin, UpdateView):
    """레슨 수정 뷰"""

    model = Lesson
    template_name = "courses/lesson_edit.html"
    form_class = LessonForm

    def get_success_url(self):
        return reverse_lazy("courses:course_edit", kwargs={"pk": self.object.section.course.id})


class LessonDeleteView(View):
    """레슨 삭제"""

    def get(self, request, pk):
        lesson = Lesson.objects.get(pk=pk)
        course_id = lesson.section.course.id
        lesson.delete()
        messages.success(request, "레슨이 삭제되었습니다.")
        return redirect("courses:course_edit", pk=course_id)
