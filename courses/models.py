from django.db import models

from accounts.models import User


class Course(models.Model):
    instructor = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.PositiveIntegerField(default=0)
    discount_price = models.PositiveIntegerField(null=True, blank=True)
    is_free = models.BooleanField(default=False)
    # thumbnail = models.ImageField(upload_to='thumbnails/')  # 나중에 추가

    STATUS_CHOICES = [
        ("draft", "초안"),
        ("review", "검토 중"),
        ("published", "출시됨"),
    ]
    status = models.CharField(max_length=11, choices=STATUS_CHOICES, default="draft")

    ACCESS_CHOICES = [
        ("purchase", "구매"),
        ("subscription", "구독"),
    ]
    access_type = models.CharField(max_length=12, choices=ACCESS_CHOICES, default="purchase")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # ✅ 가격 검증 로직 추가
        if self.discount_price and self.discount_price > self.price:
            raise ValueError("할인 가격은 원래 가격보다 높을 수 없습니다.")

        # ✅ 자동으로 is_free 설정
        self.is_free = self.price == 0

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Section(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="sections")
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Lesson(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=255)
    video_url = models.CharField(max_length=500, null=True, blank=True)
    duration = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    order = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.section.title} - {self.title}"
