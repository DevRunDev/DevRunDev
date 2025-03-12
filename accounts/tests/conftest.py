import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def student_user():
    """기본 학생 사용자 픽스처"""
    return User.objects.create_user(email="student@example.com", username="student", password="password123")


@pytest.fixture
def instructor_user():
    """기본 강사 사용자 픽스처"""
    return User.objects.create_user(
        email="instructor@example.com",
        username="instructor",
        password="password123",
        role=User.Role.INSTRUCTOR,
    )


@pytest.fixture
def admin_user():
    """관리자 사용자 픽스처"""
    return User.objects.create_superuser(email="admin@example.com", username="admin", password="adminpass123")
