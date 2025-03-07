from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "Student", "학생"
        INSTRUCTOR = "Instructor", "강사"
        MANAGER = "manager", "관리자"

    is_verified = models.BooleanField(default=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.STUDENT)
    email = models.EmailField(("email address"), unique=True)
    username = models.CharField(max_length=150, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def is_student(self):
        return self.role == self.Role.STUDENT

    def is_instructor(self):
        return self.role == self.Role.INSTRUCTOR


class InstructorApplication(models.Model):
    """강사 신청 모델"""

    class Status(models.TextChoices):
        PENDING = "PENDING", "대기 중"
        APPROVED = "APPROVED", "승인됨"
        REJECTED = "REJECTED", "거부됨"

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="instructor_applications"
    )
    qualifications = models.TextField()
    experience = models.TextField()
    sample_video_url = models.URLField(blank=True)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.status}"

    def approve(self):

        self.status = self.Status.APPROVED
        self.save()

        self.user.role = User.Role.INSTRUCTOR
        self.user.save()
