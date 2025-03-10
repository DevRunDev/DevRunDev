from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
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
        return Course.objects.filter(status="approved")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        sections = Section.objects.filter(course=course).order_by("order")

        for section in sections:
            section.lessons_list = Lesson.objects.filter(section=section).order_by("order")

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
        return render(request, "courses/course_step2.html", {"form": form})

    def post(self, request):
        form = SectionForm(request.POST)
        if form.is_valid():
            request.session["section_data"] = form.cleaned_data
            return redirect("courses:course_step3")
        return render(request, "courses/course_step2.html", {"form": form})


class CourseStep3View(LoginRequiredMixin, View):
    """레슨 정보 입력 및 강의 저장 (3단계)"""

    def dispatch(self, request, *args, **kwargs):
        if "course_data" not in request.session or "section_data" not in request.session:
            return redirect("courses:course_step1")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = LessonForm()
        return render(request, "courses/course_step3.html", {"form": form})

    def post(self, request):
        form = LessonForm(request.POST)
        if form.is_valid():
            # ✅ 세션에서 데이터 가져오기
            course_data = request.session["course_data"]
            section_data = request.session["section_data"]
            lesson_data = form.cleaned_data

            # ✅ Course, Section, Lesson 순서대로 저장
            course = Course.objects.create(
                instructor=request.user,
                title=course_data["title"],
                description=course_data["description"],
                price=course_data["price"],
                status="review",  # ✅ 승인 요청 상태로 저장
            )

            section = Section.objects.create(course=course, title=section_data["title"])

            Lesson.objects.create(
                section=section,
                title=lesson_data["title"],
                video_url=lesson_data["video_url"],
            )

            # ✅ 데이터 저장 후 세션 삭제
            del request.session["course_data"]
            del request.session["section_data"]

            messages.success(request, "강의가 성공적으로 생성되었으며, 현재 심사 중입니다.")
            return redirect("courses:course_list")

        return render(request, "courses/course_step3.html", {"form": form})


class CourseUpdateView(LoginRequiredMixin, UpdateView):
    model = Course
    template_name = "courses/course_form.html"
    form_class = CourseForm
    success_url = reverse_lazy("courses:course_list")

    def dispatch(self, request, *args, **kwargs):
        course = self.get_object()
        if course.status == "approved":
            messages.error(request, "승인된 강의는 수정할 수 없습니다.")
            return redirect("courses:course_list")
        elif course.status != "not_approved":
            messages.error(request, "승인되지 않은 강의만 수정할 수 있습니다.")
            return redirect("courses:course_list")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        course = form.save(commit=False)
        course.status = "review"
        course.save()
        messages.success(self.request, "강의 수정이 완료되었습니다. 다시 심사를 요청하세요.")
        return super().form_valid(form)
