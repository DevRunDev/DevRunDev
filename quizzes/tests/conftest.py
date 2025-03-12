import pytest
from django.contrib.auth import get_user_model

from courses.models import Course, Lesson, Section
from quizzes.models import Choice, Question, Quiz, QuizAttempt

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
def student_user():
    """기본 학생 사용자 픽스처"""
    return User.objects.create_user(
        email="student@example.com",
        username="student",
        password="password123",
        role=User.Role.STUDENT,
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


@pytest.fixture
def quiz(instructor_user, sample_course):
    """기본 퀴즈 픽스처"""
    return Quiz.objects.create(
        title="테스트 퀴즈",
        description="테스트 퀴즈 설명입니다.",
        course=sample_course,
        instructor=instructor_user,
    )


@pytest.fixture
def question(quiz):
    """기본 질문 픽스처"""
    return Question.objects.create(quiz=quiz, text="테스트 질문입니다.")


@pytest.fixture
def choices(question):
    """기본 선택지 픽스처"""
    choices = [
        Choice.objects.create(question=question, text="선택지 1", is_correct=True),
        Choice.objects.create(question=question, text="선택지 2", is_correct=False),
        Choice.objects.create(question=question, text="선택지 3", is_correct=False),
        Choice.objects.create(question=question, text="선택지 4", is_correct=False),
    ]
    return choices


@pytest.fixture
def quiz_attempt(quiz, student_user):
    """기본 퀴즈 시도 픽스처"""
    return QuizAttempt.objects.create(quiz=quiz, student=student_user)
