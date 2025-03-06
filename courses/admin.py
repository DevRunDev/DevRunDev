from django.contrib import admin

from .models import Course, Section, Lesson


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "instructor", "price", "status", "created_at")
    list_filter = ("status", "access_type")
    search_fields = ("title", "instructor__username")


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order")
    list_filter = ("course",)
    search_fields = ("title", "course__title")


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "section", "order", "duration", "is_completed")
    list_filter = ("section", "is_completed")
    search_fields = ("title", "section__title")
