from django.views.generic import ListView

from .models import Course


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
