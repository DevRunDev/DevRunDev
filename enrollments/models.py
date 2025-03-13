from django.conf import settings
from django.db import models

from courses.models import Course, Lesson


class Enrollment(models.Model):
    """수강 신청 모델 (학생이 강의를 신청하고 진행 상태를 관리)"""

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    enrolled_at = models.DateTimeField(auto_now_add=True)  # 수강 신청 날짜
    progress = models.FloatField(default=0.0)  # 강의 전체 진행률 (0% ~ 100%)
    status = models.CharField(
        max_length=20, choices=[("in_progress", "수강 중"), ("completed", "완료")], default="in_progress"
    )
    last_watched_lesson = models.ForeignKey(
        Lesson, on_delete=models.SET_NULL, null=True, blank=True, related_name="last_watched"
    )  # 마지막으로 본 레슨 (이어보기 기능)

    class Meta:
        unique_together = ("student", "course")  # 중복 수강 방지

    def update_progress(self):
        """✅ 전체 강의 진행률 업데이트 (수강한 레슨 기준)"""
        total_lessons = self.course.lessons.count()
        completed_lessons = LessonProgress.objects.filter(
            student=self.student, lesson__course=self.course, completed=True
        ).count()

        if total_lessons > 0:
            self.progress = (completed_lessons / total_lessons) * 100
        else:
            self.progress = 0

        if self.progress == 100:
            self.status = "completed"  # 강의가 모두 완료되면 상태 변경
        self.save()

    def update_last_watched(self, lesson):
        """✅ 마지막 학습한 레슨을 업데이트 (이어보기 기능)"""
        self.last_watched_lesson = lesson
        self.save()

    def re_enroll(self):
        """✅ 강의 재수강 기능 (완료 후 다시 학습 가능)"""
        self.progress = 0
        self.status = "in_progress"
        LessonProgress.objects.filter(student=self.student, lesson__course=self.course).update(completed=False)
        self.save()

    def __str__(self):
        return f"{self.student.username} - {self.course.title} ({self.status})"


class LessonProgress(models.Model):
    """✅ 레슨 학습 진행 모델 (학생이 특정 레슨을 완료했는지 기록)"""

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="lesson_progress")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="progress")
    completed = models.BooleanField(default=False)  # 레슨 완료 여부
    last_watched_at = models.DateTimeField(auto_now=True)  # 마지막 학습 시간

    class Meta:
        unique_together = ("student", "lesson")  # 같은 레슨을 중복 저장 방지

    def __str__(self):
        return f"{self.student.username} - {self.lesson.title} ({'완료' if self.completed else '진행 중'})"
