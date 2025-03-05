from django.db import models
from accounts.models import User


class Course(models.Model):
    instructor = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.PositiveIntegerField(default=0)
    discount_price = models.PositiveIntegerField(null=True, blank=True)

    STATUS_CHOICES = [
        ("draft", "초안"),
        ("review", "검토 중"),
        ("published", "출시됨"),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="draft")

    ACCESS_CHOICES = [
        ("purchase", "구매"),
        ("subscription", "구독"),
    ]
    access_type = models.CharField(
        max_length=12, choices=ACCESS_CHOICES, default="purchase"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
