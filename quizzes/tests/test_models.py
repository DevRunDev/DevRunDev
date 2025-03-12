import pytest
from django.db import IntegrityError
from django.utils import timezone

from accounts.models import User
from courses.models import Course, Lesson, Section
from quizzes.models import Answer, Choice, Question, Quiz, QuizAttempt

pytestmark = pytest.mark.django_db


class TestQuizModel:
    """Quiz 모델 테스트"""

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
    def lesson(self, section):
        """레슨 픽스처"""
        return Lesson.objects.create(
            section=section,
            title="파이썬 설치하기",
            video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        )

    @pytest.fixture
    def quiz_data(self, course, section, lesson, instructor):
        """기본 퀴즈 데이터 픽스처"""
        return {
            "title": "파이썬 기초 퀴즈",
            "description": "파이썬 설치와 환경설정에 대한 이해도를 테스트합니다.",
            "course": course,
            "section": section,
            "lesson": lesson,
            "instructor": instructor,
        }

    def test_create_quiz(self, quiz_data):
        """퀴즈 생성 테스트"""
        quiz = Quiz.objects.create(**quiz_data)

        assert quiz.title == quiz_data["title"]
        assert quiz.description == quiz_data["description"]
        assert quiz.course == quiz_data["course"]
        assert quiz.section == quiz_data["section"]
        assert quiz.lesson == quiz_data["lesson"]
        assert quiz.instructor == quiz_data["instructor"]
        assert quiz.created_at is not None
        assert quiz.updated_at is not None

    def test_quiz_string_representation(self, quiz_data):
        """__str__ 메소드 테스트"""
        quiz = Quiz.objects.create(**quiz_data)
        expected_str = f"{quiz_data['title']} - {quiz_data['course'].title}"
        assert str(quiz) == expected_str

    def test_quiz_without_section_and_lesson(self, quiz_data):
        """섹션과 레슨 없는 퀴즈 생성 테스트"""
        # 섹션과 레슨 필드는 선택사항이므로 없이도 생성 가능해야 함
        quiz_data.pop("section")
        quiz_data.pop("lesson")

        quiz = Quiz.objects.create(**quiz_data)
        assert quiz.section is None
        assert quiz.lesson is None
        assert quiz.title == quiz_data["title"]

    def test_quiz_ordering(self, quiz_data, instructor, course):
        """퀴즈 정렬 순서 테스트"""
        # 첫 번째 퀴즈 생성
        first_quiz = Quiz.objects.create(**quiz_data)

        # 두 번째 퀴즈 생성 (1초 후)
        import time

        time.sleep(1)

        second_quiz = Quiz.objects.create(
            title="두 번째 퀴즈",
            description="두 번째 퀴즈입니다.",
            course=course,
            instructor=instructor,
        )

        # 정렬 순서 확인 (최신순)
        quizzes = Quiz.objects.all()
        assert quizzes[0] == second_quiz
        assert quizzes[1] == first_quiz

    def test_quiz_cascade_delete(self, quiz_data):
        """연관 모델 삭제 시 퀴즈 캐스케이드 삭제 테스트"""
        quiz = Quiz.objects.create(**quiz_data)
        course_id = quiz.course.id

        # 코스 삭제
        Course.objects.get(id=course_id).delete()

        # 퀴즈도 함께 삭제되었는지 확인
        assert Quiz.objects.filter(id=quiz.id).count() == 0


class TestQuestionModel:
    """Question 모델 테스트"""

    @pytest.fixture
    def quiz(self, instructor_user, sample_course):
        """퀴즈 픽스처"""
        return Quiz.objects.create(
            title="테스트 퀴즈",
            description="테스트 퀴즈입니다",
            course=sample_course,
            instructor=instructor_user,
        )

    @pytest.fixture
    def question_data(self, quiz):
        """기본 질문 데이터 픽스처"""
        return {"quiz": quiz, "text": "파이썬에서 변수를 선언하는 방법은?"}

    def test_create_question(self, question_data):
        """질문 생성 테스트"""
        question = Question.objects.create(**question_data)

        assert question.quiz == question_data["quiz"]
        assert question.text == question_data["text"]
        assert question.order == 1  # 자동으로 설정된 순서

    def test_question_string_representation(self, question_data):
        """__str__ 메소드 테스트"""
        question = Question.objects.create(**question_data)
        expected_str = f"문제 {question.order}: {question.text[:50]}..."
        assert str(question) == expected_str

    def test_auto_order_assignment(self, quiz):
        """순서 자동 할당 테스트"""
        # 첫 번째 질문 생성
        question1 = Question.objects.create(quiz=quiz, text="첫 번째 질문")
        assert question1.order == 1

        # 두 번째 질문 생성
        question2 = Question.objects.create(quiz=quiz, text="두 번째 질문")
        assert question2.order == 2

        # 세 번째 질문 생성
        question3 = Question.objects.create(quiz=quiz, text="세 번째 질문")
        assert question3.order == 3

    def test_manual_order_assignment(self, quiz):
        """수동 순서 할당 테스트"""
        # 수동으로 순서 지정
        question = Question.objects.create(quiz=quiz, text="수동 순서 질문", order=5)
        assert question.order == 5

    def test_question_ordering(self, quiz):
        """질문 정렬 순서 테스트"""
        # 순서가 다른 여러 질문 생성
        question3 = Question.objects.create(quiz=quiz, text="세 번째 질문", order=3)
        question1 = Question.objects.create(quiz=quiz, text="첫 번째 질문", order=1)
        question2 = Question.objects.create(quiz=quiz, text="두 번째 질문", order=2)

        # 정렬 순서 확인
        questions = quiz.questions.all()
        assert questions[0] == question1
        assert questions[1] == question2
        assert questions[2] == question3


class TestChoiceModel:
    """Choice 모델 테스트"""

    @pytest.fixture
    def question(self, quiz):
        """질문 픽스처"""
        return Question.objects.create(quiz=quiz, text="파이썬에서 변수를 선언하는 방법은?")

    @pytest.fixture
    def choice_data(self, question):
        """기본 선택지 데이터 픽스처"""
        return {"question": question, "text": "변수명 = 값", "is_correct": True}

    def test_create_choice(self, choice_data):
        """선택지 생성 테스트"""
        choice = Choice.objects.create(**choice_data)

        assert choice.question == choice_data["question"]
        assert choice.text == choice_data["text"]
        assert choice.is_correct == choice_data["is_correct"]

    def test_choice_string_representation(self, choice_data):
        """__str__ 메소드 테스트"""
        choice = Choice.objects.create(**choice_data)
        expected_str = f"{choice.text} - {'정답' if choice.is_correct else '오답'}"
        assert str(choice) == expected_str

    def test_multiple_choices_for_question(self, question):
        """하나의 질문에 여러 선택지 생성 테스트"""
        # 4개의 선택지 생성
        choice1 = Choice.objects.create(question=question, text="변수명 = 값", is_correct=True)
        choice2 = Choice.objects.create(question=question, text="var 변수명 = 값", is_correct=False)
        choice3 = Choice.objects.create(question=question, text="let 변수명 = 값", is_correct=False)
        choice4 = Choice.objects.create(question=question, text="const 변수명 = 값", is_correct=False)

        # 질문에 연결된 모든 선택지 확인
        choices = question.choices.all()
        assert choices.count() == 4
        assert set(choices) == {choice1, choice2, choice3, choice4}

    def test_multiple_correct_choices(self, question):
        """여러 개의 정답 선택지 테스트"""
        # 두 개의 정답 선택지 생성
        choice1 = Choice.objects.create(question=question, text="정답 1", is_correct=True)
        choice2 = Choice.objects.create(question=question, text="정답 2", is_correct=True)

        # 정답 선택지 수 확인
        correct_choices = question.choices.filter(is_correct=True)
        assert correct_choices.count() == 2
        assert set(correct_choices) == {choice1, choice2}


class TestQuizAttemptModel:
    """QuizAttempt 모델 테스트"""

    @pytest.fixture
    def student(self):
        """학생 사용자 픽스처"""
        return User.objects.create_user(
            email="student@example.com",
            username="student",
            password="password123",
            role=User.Role.STUDENT,
        )

    @pytest.fixture
    def quiz_with_questions(self, quiz):
        """문제가 있는 퀴즈 픽스처"""
        # 2개의 질문 생성
        question1 = Question.objects.create(quiz=quiz, text="질문 1")
        question2 = Question.objects.create(quiz=quiz, text="질문 2")

        # 각 질문에 선택지 생성
        Choice.objects.create(question=question1, text="선택지 1-1", is_correct=True)
        Choice.objects.create(question=question1, text="선택지 1-2", is_correct=False)

        Choice.objects.create(question=question2, text="선택지 2-1", is_correct=False)
        Choice.objects.create(question=question2, text="선택지 2-2", is_correct=True)

        return quiz

    @pytest.fixture
    def quiz_attempt_data(self, quiz_with_questions, student):
        """기본 퀴즈 시도 데이터 픽스처"""
        return {"quiz": quiz_with_questions, "student": student}

    def test_create_quiz_attempt(self, quiz_attempt_data):
        """퀴즈 시도 생성 테스트"""
        attempt = QuizAttempt.objects.create(**quiz_attempt_data)

        assert attempt.quiz == quiz_attempt_data["quiz"]
        assert attempt.student == quiz_attempt_data["student"]
        assert attempt.started_at is not None
        assert attempt.completed_at is None
        assert attempt.score == 0
        assert attempt.total_questions == 0
        assert attempt.correct_answers == 0
        assert attempt.is_completed is False

    def test_quiz_attempt_string_representation(self, quiz_attempt_data):
        """__str__ 메소드 테스트"""
        attempt = QuizAttempt.objects.create(**quiz_attempt_data)
        expected_str = f"{attempt.student.email} - {attempt.quiz.title} ({attempt.score}점)"
        assert str(attempt) == expected_str

    def test_calculate_score_no_answers(self, quiz_attempt_data):
        """답변 없는 점수 계산 테스트"""
        attempt = QuizAttempt.objects.create(**quiz_attempt_data)

        # 답변 없이 점수 계산
        attempt.calculate_score()
        assert attempt.score == 0

    def test_calculate_score_with_answers(self, quiz_attempt_data):
        """답변 있는 점수 계산 테스트"""
        attempt = QuizAttempt.objects.create(**quiz_attempt_data)

        # 총 문제 수와 정답 수 수동 설정
        attempt.total_questions = 4
        attempt.correct_answers = 3

        # 점수 계산 (3/4 = 75%)
        attempt.calculate_score()
        assert attempt.score == 75

    def test_quiz_attempt_ordering(self, quiz_attempt_data, student, quiz_with_questions):
        """퀴즈 시도 정렬 순서 테스트"""
        # 첫 번째 시도 생성
        first_attempt = QuizAttempt.objects.create(**quiz_attempt_data)

        # 두 번째 시도 생성 (1초 후)
        import time

        time.sleep(1)

        second_attempt = QuizAttempt.objects.create(quiz=quiz_with_questions, student=student)

        # 정렬 순서 확인 (최신순)
        attempts = QuizAttempt.objects.all()
        assert attempts[0] == second_attempt
        assert attempts[1] == first_attempt

    def test_complete_quiz_attempt(self, quiz_attempt_data):
        """퀴즈 시도 완료 테스트"""
        attempt = QuizAttempt.objects.create(**quiz_attempt_data)

        # 완료 처리
        attempt.is_completed = True
        attempt.completed_at = timezone.now()
        attempt.save()

        # DB에서 다시 조회
        refreshed_attempt = QuizAttempt.objects.get(id=attempt.id)
        assert refreshed_attempt.is_completed is True
        assert refreshed_attempt.completed_at is not None


class TestAnswerModel:
    """Answer 모델 테스트"""

    @pytest.fixture
    def question_with_choices(self, quiz):
        """선택지가 있는 질문 픽스처"""
        question = Question.objects.create(quiz=quiz, text="파이썬에서 변수를 선언하는 방법은?")

        # 선택지 생성
        Choice.objects.create(question=question, text="var x = 10", is_correct=False)
        Choice.objects.create(question=question, text="let x = 10", is_correct=False)
        Choice.objects.create(question=question, text="x = 10", is_correct=True)
        Choice.objects.create(question=question, text="const x = 10", is_correct=False)

        return question

    @pytest.fixture
    def quiz_attempt(self, quiz, student_user):
        """퀴즈 시도 픽스처"""
        return QuizAttempt.objects.create(quiz=quiz, student=student_user)

    @pytest.fixture
    def answer_data(self, quiz_attempt, question_with_choices):
        """기본 답변 데이터 픽스처"""
        correct_choice = question_with_choices.choices.get(is_correct=True)
        return {
            "attempt": quiz_attempt,
            "question": question_with_choices,
            "selected_choice": correct_choice,
        }

    def test_create_answer(self, answer_data):
        """답변 생성 테스트"""
        answer = Answer.objects.create(**answer_data)

        assert answer.attempt == answer_data["attempt"]
        assert answer.question == answer_data["question"]
        assert answer.selected_choice == answer_data["selected_choice"]
        assert answer.is_correct is True  # 정답을 선택했으므로 True

    def test_answer_string_representation(self, answer_data):
        """__str__ 메소드 테스트"""
        answer = Answer.objects.create(**answer_data)
        expected_str = f"{answer.attempt.student.email}의 {answer.question}에 대한 답변"
        assert str(answer) == expected_str

    def test_auto_is_correct_assignment(self, quiz_attempt, question_with_choices):
        """자동 정답 여부 설정 테스트"""
        # 오답 선택
        wrong_choice = question_with_choices.choices.filter(is_correct=False).first()
        wrong_answer = Answer.objects.create(
            attempt=quiz_attempt,
            question=question_with_choices,
            selected_choice=wrong_choice,
        )
        assert wrong_answer.is_correct is False

        # 정답 선택
        _ = question_with_choices.choices.get(is_correct=True)
        correct_answer = Answer.objects.create(
            attempt=quiz_attempt,
            question=Question.objects.create(quiz=quiz_attempt.quiz, text="다른 질문"),
            selected_choice=Choice.objects.create(
                question=Question.objects.get(text="다른 질문"),
                text="정답",
                is_correct=True,
            ),
        )
        assert correct_answer.is_correct is True

    def test_update_quiz_attempt_on_answer_save(self, answer_data, quiz_attempt, question_with_choices):
        """답변 저장 시 퀴즈 시도 업데이트 테스트"""
        # 초기 상태 확인
        assert quiz_attempt.correct_answers == 0
        assert quiz_attempt.total_questions == 0
        assert quiz_attempt.score == 0

        # 정답 생성
        Answer.objects.create(**answer_data)

        # 퀴즈 시도가 업데이트되었는지 확인
        refreshed_attempt = QuizAttempt.objects.get(id=quiz_attempt.id)
        assert refreshed_attempt.correct_answers == 1
        assert refreshed_attempt.total_questions == 1
        assert refreshed_attempt.score == 100  # 1/1 = 100%

        # 오답 추가
        _ = question_with_choices.choices.filter(is_correct=False).first()
        another_question = Question.objects.create(quiz=quiz_attempt.quiz, text="다른 질문")

        # 다른 질문에 대한 오답 생성
        _ = Answer.objects.create(
            attempt=quiz_attempt,
            question=another_question,
            selected_choice=Choice.objects.create(question=another_question, text="오답", is_correct=False),
        )

        # 다시 퀴즈 시도 확인
        refreshed_attempt = QuizAttempt.objects.get(id=quiz_attempt.id)
        assert refreshed_attempt.correct_answers == 1
        assert refreshed_attempt.total_questions == 2
        assert refreshed_attempt.score == 50  # 1/2 = 50%

    def test_unique_answer_per_question_per_attempt(self, answer_data):
        """하나의 시도에서 하나의 질문에 하나의 답변만 허용 테스트"""
        # 첫 번째 답변 생성
        Answer.objects.create(**answer_data)

        # 같은 시도, 같은 질문에 대한 두 번째 답변 생성 시도
        with pytest.raises(IntegrityError):
            Answer.objects.create(
                attempt=answer_data["attempt"],
                question=answer_data["question"],
                selected_choice=answer_data["question"].choices.filter(is_correct=False).first(),
            )
