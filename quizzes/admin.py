# quizzes/admin.py
from django.contrib import admin
from .models import Quiz, Question, Choice, QuizAttempt, Answer


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 5  # 5지선다이므로 5개의 선택지를 기본으로 표시
    max_num = 5  # 최대 5개까지만 추가 가능


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "quiz", "order")
    list_filter = ("quiz",)
    search_fields = ("text", "quiz__title")
    inlines = [ChoiceInline]


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "created_at")
    list_filter = ("course",)
    search_fields = ("title", "description", "course__title")
    date_hierarchy = "created_at"
    inlines = [QuestionInline]


class AnswerInline(admin.TabularInline):
    model = Answer
    readonly_fields = ("question", "selected_choice", "is_correct")
    extra = 0  # 추가 입력 칸 없음
    can_delete = False  # 삭제 불가


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ("student", "quiz", "started_at", "completed_at", "score")
    list_filter = ("quiz", "started_at")
    search_fields = ("student__username", "quiz__title")
    readonly_fields = ("score",)
    inlines = [AnswerInline]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("attempt", "question", "selected_choice", "is_correct")
    list_filter = ("is_correct", "attempt__quiz")
    search_fields = ("attempt__student__username", "question__text")
