from django.views.generic import DetailView, ListView

from .models import Course, Section


class CourseListView(ListView):
    model = Course
    template_name = "courses/course_list.html"
    context_object_name = "courses"
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = Course.objects.filter(status="published")

        search_query = self.request.GET.get("q")
        if search_query:
            queryset = queryset.filter(title__icontains=search_query)

        return queryset


class CourseDetailView(DetailView):
    model = Course
    template_name = "courses/course_detail.html"
    context_object_name = "course"

    def get_queryset(self):
        return Course.objects.filter(status="published")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()

        context["sections"] = Section.objects.filter(course=course).order_by("order")

        return context
