import pytest
from django.contrib.auth import get_user_model

from courses.models import Course, Lesson, Section

User = get_user_model()


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
def sample_course(instructor_user):
    """기본 코스 픽스처"""
    return Course.objects.create(
        instructor=instructor_user,
        title="테스트 코스",
        description="테스트 코스 설명입니다.",
        price=15000,
    )


@pytest.fixture
def sample_section(sample_course):
    """기본 섹션 픽스처"""
    return Section.objects.create(course=sample_course, title="테스트 섹션")


@pytest.fixture
def sample_lesson(sample_section):
    """기본 레슨 픽스처"""
    return Lesson.objects.create(
        section=sample_section,
        title="테스트 레슨",
        video_url="https://www.youtube.com/watch?v=test123",
    )
