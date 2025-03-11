from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, ListView, UpdateView

from .forms import CourseForm, LessonForm, SectionForm
from .models import Course, Lesson, Section


class CourseListView(ListView):
    model = Course
    template_name = "courses/course_list.html"
    context_object_name = "courses"
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = Course.objects.filter(status="approved")
        search_query = self.request.GET.get("q")
        if search_query:
            queryset = queryset.filter(title__icontains=search_query)
        return queryset


class CourseDetailView(DetailView):
    model = Course
    template_name = "courses/course_detail.html"
    context_object_name = "course"

    def get_queryset(self):
        """강사는 자신의 강의를 모두 조회 가능, 일반 사용자는 승인된 강의만 조회 가능"""
        queryset = Course.objects.all()
        if not self.request.user.is_authenticated or not self.request.user.is_instructor:
            queryset = queryset.filter(status="approved")
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        sections = Section.objects.filter(course=course).order_by("order")

        for section in sections:
            section.lessons_list = Lesson.objects.filter(section=section).order_by(
                "order"
            )

        context["sections"] = sections
        return context


class LessonDetailView(DetailView):
    model = Lesson
    template_name = "courses/lesson_detail.html"
    context_object_name = "lesson"

    def get_queryset(self):
        return Lesson.objects.all()


class CourseStep1View(LoginRequiredMixin, View):
    """강의 기본 정보 입력 (1단계)"""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_instructor():
            messages.error(
                request, "강의 생성은 강사만 가능합니다. 강사 계정으로 로그인해주세요."
            )
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
        if (
            "course_data" not in request.session
            or "section_data" not in request.session
        ):
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

        course_data = request.session["course_data"]
        section_data = request.session["section_data"]
        lesson_data = request.session.get("lesson_data", {})

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

        messages.success(request, "강의가 성공적으로 생성되었으며, 현재 심사 중입니다.")
        return redirect("courses:course_list")


class InstructorDashboardView(LoginRequiredMixin, View):
    """강사 대시보드 - 내 강의 목록 및 상태별 필터링"""

    def get(self, request):
        if not request.user.is_instructor():
            messages.error(
                request,
                "강사만 접근할 수 있는 페이지입니다. 강사 계정으로 로그인해주세요.",
            )
            return redirect("courses:course_list")

        status_filter = request.GET.get("status")
        courses = Course.objects.filter(instructor=request.user)


        if status_filter in ["approved", "review", "not_approved"]:
            courses = courses.filter(status=status_filter)

        # ✅ 최적화된 상태별 개수 조회 (한 번의 쿼리로 가져오기)
        course_counts = Course.objects.filter(instructor=request.user).values("status").annotate(count=Count("status"))
        status_counts = {item["status"]: item["count"] for item in course_counts}


        context = {
            "courses": courses,
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
