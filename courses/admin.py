from django.contrib import admin
from .models import Course


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "instructor", "price", "status", "created_at")
    list_filter = ("status", "access_type")
    search_fields = ("title", "instructor__username")
