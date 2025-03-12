import pytest
from django.db import IntegrityError

from accounts.models import InstructorApplication, User

pytestmark = pytest.mark.django_db


class TestUserModel:
    """User 모델 테스트"""

    def test_create_user(self):
        """기본 사용자 생성 테스트"""
        user = User.objects.create_user(email="test@example.com", username="testuser", password="password123")
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.role == User.Role.STUDENT
        assert user.is_verified is True
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False

    def test_create_superuser(self):
        """관리자 사용자 생성 테스트"""
        admin = User.objects.create_superuser(email="admin@example.com", username="admin", password="adminpass123")
        assert admin.email == "admin@example.com"
        assert admin.is_staff is True
        assert admin.is_superuser is True
        assert admin.role == User.Role.MANAGER  # 슈퍼유저는 자동으로 MANAGER 역할 부여 예상

    def test_email_unique_constraint(self):
        """이메일 유니크 제약 조건 테스트"""
        User.objects.create_user(email="duplicate@example.com", username="user1", password="password123")

        # 같은 이메일로 사용자 생성 시도
        with pytest.raises(IntegrityError):
            User.objects.create_user(email="duplicate@example.com", username="user2", password="password456")

    def test_required_email(self):
        """이메일 필수 필드 테스트"""
        with pytest.raises(ValueError):
            User.objects.create_user(email="", username="testuser", password="password123")

    def test_user_str_method(self):
        """__str__ 메소드 테스트"""
        user = User.objects.create_user(email="test@example.com", username="testuser", password="password123")
        assert str(user) == "test@example.com"

    def test_is_student_method(self):
        """is_student 메소드 테스트"""
        student = User.objects.create_user(
            email="student@example.com",
            username="student",
            password="password123",
            role=User.Role.STUDENT,
        )
        instructor = User.objects.create_user(
            email="instructor@example.com",
            username="instructor",
            password="password123",
            role=User.Role.INSTRUCTOR,
        )

        assert student.is_student() is True
        assert instructor.is_student() is False

    def test_is_instructor_method(self):
        """is_instructor 메소드 테스트"""
        student = User.objects.create_user(
            email="student@example.com",
            username="student",
            password="password123",
            role=User.Role.STUDENT,
        )
        instructor = User.objects.create_user(
            email="instructor@example.com",
            username="instructor",
            password="password123",
            role=User.Role.INSTRUCTOR,
        )

        assert student.is_instructor() is False
        assert instructor.is_instructor() is True


class TestInstructorApplicationModel:
    """InstructorApplication 모델 테스트"""

    @pytest.fixture
    def student_user(self):
        """학생 사용자 픽스처"""
        return User.objects.create_user(email="student@example.com", username="student", password="password123")

    @pytest.fixture
    def application_data(self):
        """강사 신청 데이터 픽스처"""
        return {
            "qualifications": "컴퓨터 공학 학사",
            "experience": "3년차 백엔드 개발자",
            "sample_video_url": "https://example.com/sample-video",
        }

    def test_create_instructor_application(self, student_user, application_data):
        """강사 신청 생성 테스트"""
        application = InstructorApplication.objects.create(user=student_user, **application_data)

        assert application.user == student_user
        assert application.qualifications == application_data["qualifications"]
        assert application.experience == application_data["experience"]
        assert application.sample_video_url == application_data["sample_video_url"]
        assert application.status == InstructorApplication.Status.PENDING
        assert application.created_at is not None
        assert application.updated_at is not None

    def test_approve_method(self, student_user, application_data):
        """강사 신청 승인 메소드 테스트"""
        application = InstructorApplication.objects.create(user=student_user, **application_data)

        # 초기 상태 확인
        assert application.status == InstructorApplication.Status.PENDING
        assert student_user.role == User.Role.STUDENT

        # 승인 처리
        application.approve()

        # DB에서 다시 조회하여 변경사항 확인
        refreshed_application = InstructorApplication.objects.get(id=application.id)
        refreshed_user = User.objects.get(id=student_user.id)

        assert refreshed_application.status == InstructorApplication.Status.APPROVED
        assert refreshed_user.role == User.Role.INSTRUCTOR

    def test_multiple_applications_same_user(self, student_user, application_data):
        """동일 사용자의 여러 신청 테스트"""
        # 첫 번째 신청
        InstructorApplication.objects.create(user=student_user, **application_data)

        # 동일 사용자의 두 번째 신청
        second_application = InstructorApplication.objects.create(
            user=student_user,
            qualifications="업데이트된 자격",
            experience="업데이트된 경험",
        )

        # 해당 사용자의 모든 신청 조회
        applications = InstructorApplication.objects.filter(user=student_user)
        assert applications.count() == 2

        # 최신 신청 확인
        assert applications.order_by("-created_at").first().id == second_application.id

    def test_str_method(self, student_user, application_data):
        """__str__ 메소드 테스트"""
        application = InstructorApplication.objects.create(user=student_user, **application_data)
        expected_str = f"{student_user.email} - {InstructorApplication.Status.PENDING}"
        assert str(application) == expected_str

    def test_status_transitions(self, student_user, application_data):
        """상태 전이 테스트"""
        application = InstructorApplication.objects.create(user=student_user, **application_data)

        # PENDING -> REJECTED 상태 변경
        application.status = InstructorApplication.Status.REJECTED
        application.save()
        assert application.status == InstructorApplication.Status.REJECTED

        # REJECTED -> APPROVED 상태 변경
        application.status = InstructorApplication.Status.APPROVED
        application.save()
        assert application.status == InstructorApplication.Status.APPROVED
