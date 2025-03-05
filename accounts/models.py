from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    is_verified = models.BooleanField(default=True)
    ROLE_CHOICES = [("Student", "학생"), ("Teacher", "강사"), ("manager", "관리자")]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
