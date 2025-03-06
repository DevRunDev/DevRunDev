from django.contrib import admin

from .models import Course, Lesson, Section


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "instructor", "price", "is_free", "status", "created_at")
    list_filter = ("status", "access_type", "is_free")
    search_fields = ("title", "instructor__username")
    ordering = ("-created_at",)


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order")
    list_filter = ("course",)
    search_fields = ("title", "course__title")
    ordering = ("course", "order")


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "section", "order", "duration", "is_completed")
    list_filter = ("section", "is_completed")
    search_fields = ("title", "section__title")
    ordering = ("section", "order")
