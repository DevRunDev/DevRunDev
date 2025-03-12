import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from accounts.models import User
from courses.models import Course, Lesson, Section

pytestmark = pytest.mark.django_db


class TestCourseModel:
    """Course 모델 테스트"""

    @pytest.fixture
    def instructor(self):
        """강사 사용자 픽스처"""
        return User.objects.create_user(
            email="instructor@example.com",
            username="instructor",
            password="password123",
            role=User.Role.INSTRUCTOR,
        )

    @pytest.fixture
    def course_data(self, instructor):
        """기본 코스 데이터 픽스처"""
        return {
            "instructor": instructor,
            "title": "파이썬 기초 강의",
            "description": "파이썬 프로그래밍의 기초를 배웁니다.",
            "price": 10000,
        }

    def test_create_course(self, course_data):
        """코스 생성 테스트"""
        course = Course.objects.create(**course_data)

        assert course.title == course_data["title"]
        assert course.description == course_data["description"]
        assert course.price == course_data["price"]
        assert course.instructor == course_data["instructor"]
        assert course.status == "review"  # 기본값 확인
        assert course.created_at is not None
        assert course.updated_at is not None

    def test_course_string_representation(self, course_data):
        """__str__ 메소드 테스트"""
        course = Course.objects.create(**course_data)
        assert str(course) == course_data["title"]

    def test_course_status_choices(self, course_data):
        """상태 선택지 테스트"""
        course = Course.objects.create(**course_data)

        # 상태 변경 테스트
        for status, _ in Course.STATUS_CHOICES:
            course.status = status
            course.save()
            refreshed_course = Course.objects.get(id=course.id)
            assert refreshed_course.status == status

    def test_invalid_status_value(self, course_data):
        """유효하지 않은 상태값 테스트"""
        course = Course.objects.create(**course_data)

        # 유효하지 않은 상태로 변경 시도
        course.status = "invalid_status"

        # Django의 full_clean이 ValidationError를 발생시키는지 확인
        with pytest.raises(ValidationError):
            course.full_clean()

    def test_price_non_negative(self, course_data, instructor):
        """가격 음수 불가 테스트"""
        # PositiveIntegerField는 음수를 저장할 수 없음을 확인
        with pytest.raises(IntegrityError):
            Course.objects.create(
                instructor=instructor,
                title="음수 가격 테스트",
                description="테스트",
                price=-1000,  # 음수 가격
            )


class TestSectionModel:
    """Section 모델 테스트"""

    @pytest.fixture
    def instructor(self):
        """강사 사용자 픽스처"""
        return User.objects.create_user(
            email="instructor@example.com",
            username="instructor",
            password="password123",
            role=User.Role.INSTRUCTOR,
        )

    @pytest.fixture
    def course(self, instructor):
        """코스 픽스처"""
        return Course.objects.create(
            instructor=instructor,
            title="파이썬 기초 강의",
            description="파이썬 프로그래밍의 기초를 배웁니다.",
            price=10000,
        )

    @pytest.fixture
    def section_data(self, course):
        """기본 섹션 데이터 픽스처"""
        return {"course": course, "title": "파이썬 설치 및 환경설정"}

    def test_create_section(self, section_data):
        """섹션 생성 테스트"""
        section = Section.objects.create(**section_data)

        assert section.title == section_data["title"]
        assert section.course == section_data["course"]
        assert section.order == 1  # 자동 설정된 순서 확인

    def test_section_string_representation(self, section_data):
        """__str__ 메소드 테스트"""
        section = Section.objects.create(**section_data)
        expected_str = f"{section_data['course'].title} - {section_data['title']}"
        assert str(section) == expected_str

    def test_auto_order_assignment(self, course):
        """순서 자동 할당 테스트"""
        # 첫 번째 섹션 생성
        section1 = Section.objects.create(course=course, title="섹션 1")
        assert section1.order == 1

        # 두 번째 섹션 생성
        section2 = Section.objects.create(course=course, title="섹션 2")
        assert section2.order == 2

        # 세 번째 섹션 생성
        section3 = Section.objects.create(course=course, title="섹션 3")
        assert section3.order == 3

    def test_manual_order_assignment(self, course):
        """수동 순서 할당 테스트"""
        # 수동으로 순서 지정
        section = Section.objects.create(course=course, title="수동 순서 섹션", order=5)
        assert section.order == 5

    def test_multiple_courses_order_isolation(self, instructor):
        """여러 코스 간 순서 격리 테스트"""
        # 두 개의 다른 코스 생성
        course1 = Course.objects.create(
            instructor=instructor,
            title="코스 1",
            description="첫 번째 코스",
            price=10000,
        )

        course2 = Course.objects.create(
            instructor=instructor,
            title="코스 2",
            description="두 번째 코스",
            price=20000,
        )

        # 각 코스에 섹션 추가
        section1_course1 = Section.objects.create(course=course1, title="코스 1의 섹션")

        section1_course2 = Section.objects.create(course=course2, title="코스 2의 섹션")

        # 각 코스의 첫 번째 섹션이 order=1을 가지는지 확인
        assert section1_course1.order == 1
        assert section1_course2.order == 1


class TestLessonModel:
    """Lesson 모델 테스트"""

    @pytest.fixture
    def instructor(self):
        """강사 사용자 픽스처"""
        return User.objects.create_user(
            email="instructor@example.com",
            username="instructor",
            password="password123",
            role=User.Role.INSTRUCTOR,
        )

    @pytest.fixture
    def course(self, instructor):
        """코스 픽스처"""
        return Course.objects.create(
            instructor=instructor,
            title="파이썬 기초 강의",
            description="파이썬 프로그래밍의 기초를 배웁니다.",
            price=10000,
        )

    @pytest.fixture
    def section(self, course):
        """섹션 픽스처"""
        return Section.objects.create(course=course, title="파이썬 설치 및 환경설정")

    @pytest.fixture
    def lesson_data(self, section):
        """기본 레슨 데이터 픽스처"""
        return {
            "section": section,
            "title": "파이썬 설치하기",
            "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        }

    def test_create_lesson(self, lesson_data):
        """레슨 생성 테스트"""
        lesson = Lesson.objects.create(**lesson_data)

        assert lesson.title == lesson_data["title"]
        assert lesson.section == lesson_data["section"]
        assert "youtube.com/embed/" in lesson.video_url  # URL 변환 확인
        assert lesson.order == 1  # 자동 설정된 순서 확인

    def test_lesson_string_representation(self, lesson_data):
        """__str__ 메소드 테스트"""
        lesson = Lesson.objects.create(**lesson_data)
        assert str(lesson) == lesson_data["title"]

    def test_auto_order_assignment(self, section):
        """순서 자동 할당 테스트"""
        # 첫 번째 레슨 생성
        lesson1 = Lesson.objects.create(
            section=section,
            title="레슨 1",
            video_url="https://www.youtube.com/watch?v=video1",
        )
        assert lesson1.order == 1

        # 두 번째 레슨 생성
        lesson2 = Lesson.objects.create(
            section=section,
            title="레슨 2",
            video_url="https://www.youtube.com/watch?v=video2",
        )
        assert lesson2.order == 2

        # 세 번째 레슨 생성
        lesson3 = Lesson.objects.create(
            section=section,
            title="레슨 3",
            video_url="https://www.youtube.com/watch?v=video3",
        )
        assert lesson3.order == 3

    def test_manual_order_assignment(self, section):
        """수동 순서 할당 테스트"""
        # 수동으로 순서 지정
        lesson = Lesson.objects.create(
            section=section,
            title="수동 순서 레슨",
            video_url="https://www.youtube.com/watch?v=manual",
            order=5,
        )
        assert lesson.order == 5

    def test_multiple_sections_order_isolation(self, course):
        """여러 섹션 간 순서 격리 테스트"""
        # 두 개의 다른 섹션 생성
        section1 = Section.objects.create(course=course, title="섹션 1")

        section2 = Section.objects.create(course=course, title="섹션 2")

        # 각 섹션에 레슨 추가
        lesson1_section1 = Lesson.objects.create(
            section=section1,
            title="섹션 1의 레슨",
            video_url="https://www.youtube.com/watch?v=section1",
        )

        lesson1_section2 = Lesson.objects.create(
            section=section2,
            title="섹션 2의 레슨",
            video_url="https://www.youtube.com/watch?v=section2",
        )

        # 각 섹션의 첫 번째 레슨이 order=1을 가지는지 확인
        assert lesson1_section1.order == 1
        assert lesson1_section2.order == 1

    def test_youtube_url_conversion(self, section):
        """유튜브 URL 변환 테스트"""
        # 다양한 유튜브 URL 형식 테스트
        test_cases = [
            {
                "input": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "expected_id": "dQw4w9WgXcQ",
            },
            {"input": "https://youtu.be/dQw4w9WgXcQ", "expected_id": "dQw4w9WgXcQ"},
            {
                "input": "https://www.youtube.com/v/dQw4w9WgXcQ",
                "expected_id": "dQw4w9WgXcQ",
            },
            {
                "input": "https://www.youtube.com/shorts/dQw4w9WgXcQ",
                "expected_id": "dQw4w9WgXcQ",
            },
        ]

        for i, test_case in enumerate(test_cases):
            lesson = Lesson.objects.create(
                section=section,
                title=f"유튜브 테스트 {i + 1}",
                video_url=test_case["input"],
            )
            expected_url = f"https://www.youtube.com/embed/{test_case['expected_id']}"
            assert lesson.video_url == expected_url

    def test_embed_url_not_converted(self, section):
        """이미 변환된 embed URL 재변환 방지 테스트"""
        embed_url = "https://www.youtube.com/embed/dQw4w9WgXcQ"
        lesson = Lesson.objects.create(section=section, title="이미 변환된 URL", video_url=embed_url)
        assert lesson.video_url == embed_url  # URL이 변경되지 않아야 함

    def test_non_youtube_url_not_converted(self, section):
        """유튜브가 아닌 URL 변환 방지 테스트"""
        non_youtube_url = "https://www.example.com/video"
        lesson = Lesson.objects.create(section=section, title="유튜브 아닌 URL", video_url=non_youtube_url)
        assert lesson.video_url == non_youtube_url  # URL이 변경되지 않아야 함

    def test_null_video_url(self, section):
        """비디오 URL이 None인 경우 테스트"""
        lesson = Lesson.objects.create(section=section, title="비디오 없는 레슨", video_url=None)
        assert lesson.video_url is None  # URL이 None으로 유지되어야 함

        # 비디오 URL을 나중에 추가했을 때 변환 확인
        lesson.video_url = "https://youtu.be/dQw4w9WgXcQ"
        lesson.save()
        assert lesson.video_url == "https://www.youtube.com/embed/dQw4w9WgXcQ"
