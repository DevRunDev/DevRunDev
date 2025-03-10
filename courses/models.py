import re

from django.db import models

from accounts.models import User


class Course(models.Model):
    STATUS_CHOICES = [
        ("review", "심사 중"),
        ("approved", "승인됨"),
        ("not_approved", "승인되지 않음"),
    ]

    instructor = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="review")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Section(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="sections")
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField()

    def save(self, *args, **kwargs):
        if not self.order:
            last_order = Section.objects.filter(course=self.course).count()
            self.order = last_order + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Lesson(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=255)
    video_url = models.CharField(max_length=500, null=True, blank=True)
    order = models.PositiveIntegerField()

    def save(self, *args, **kwargs):
        if not self.order:
            last_order = Lesson.objects.filter(section=self.section).count()
            self.order = last_order + 1

        # ✅ 유튜브 URL이 이미 변환된 상태라면 다시 변환하지 않음
        if self.video_url and "youtube.com/embed" not in self.video_url:
            youtube_regex = (
                r"(https?://)?(www\.)?"
                r"(youtube|youtu|youtube-nocookie)\.(com|be)/"
                r"(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})"
            )
            match = re.search(youtube_regex, self.video_url)
            if match:
                video_id = match.group(6)
                self.video_url = f"https://www.youtube.com/embed/{video_id}"

        super().save(*args, **kwargs)
