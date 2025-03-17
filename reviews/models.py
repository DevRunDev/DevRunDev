from django.conf import settings
from django.db import models
from django.db.models import Avg

from courses.models import Course


class Review(models.Model):
    """강의 리뷰 모델"""

    RATING_CHOICES = [(i, f"{i}점") for i in range(1, 6)]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)  # 별점 1~5
    comment = models.TextField(blank=True)  # 리뷰 내용
    created_at = models.DateTimeField(auto_now_add=True)  # 생성 시간
    updated_at = models.DateTimeField(auto_now=True)  # 수정 시간

    class Meta:
        unique_together = ("course", "user")  # 한 강의당 한 번만 리뷰 작성 가능

    def __str__(self):
        return f"{self.course.title} - {self.user.username} ({self.rating}점)"

    @staticmethod
    def get_average_rating(course):
        """강의의 평균 별점을 계산 (최적화)"""
        avg_rating = course.reviews.aggregate(avg_rating=Avg("rating"))["avg_rating"]
        return round(avg_rating, 1) if avg_rating else 0  # ⭐ 별점 없을 경우 0 반환
