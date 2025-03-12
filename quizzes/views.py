# quizzes/views.py
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, FormView,
                                  ListView, UpdateView, View)

from courses.models import Course

from .forms import AnswerForm, ChoiceFormSet, QuestionForm, QuizForm
from .models import Answer, Choice, Question, Quiz, QuizAttempt


# 강사 권한 확인 믹스인
class InstructorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_instructor()

# 퀴즈 목록 뷰
class QuizListView(LoginRequiredMixin, ListView):
    model = Quiz
    template_name = 'quizzes/quiz_list.html'
    context_object_name = 'quizzes'
    
    def get_queryset(self):
        # URL에서 강의 ID 가져오기
        course_id = self.kwargs.get('course_id')
        return Quiz.objects.filter(course_id=course_id)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 강의 정보 추가
        course_id = self.kwargs.get('course_id')
        course = get_object_or_404(Course, id=course_id)
        context['course'] = course
        
        # 현재 사용자가 강사인지 확인
        context['is_instructor'] = self.request.user.is_instructor()
        
        return context

# 퀴즈 생성 뷰
class QuizCreateView(LoginRequiredMixin, InstructorRequiredMixin, CreateView):
    model = Quiz
    form_class = QuizForm
    template_name = 'quizzes/quiz_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # 폼 초기화 시 강의 정보 전달
        course_id = self.kwargs.get('course_id')
        course = get_object_or_404(Course, id=course_id)
        kwargs['course'] = course
        return kwargs
    
    def form_valid(self, form):
        # 폼 저장 전에 강의와 강사 정보 설정
        course_id = self.kwargs.get('course_id')
        form.instance.course_id = course_id
        form.instance.instructor = self.request.user
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 강의 정보 추가
        course_id = self.kwargs.get('course_id')
        course = get_object_or_404(Course, id=course_id)
        context['course'] = course
        return context
    
    def get_success_url(self):
        # 퀴즈 생성 후 바로 문제 생성 페이지로 이동
        return reverse('quizzes:question_create', kwargs={'quiz_id': self.object.id})

# 퀴즈 상세 보기
class QuizDetailView(LoginRequiredMixin, DetailView):
    model = Quiz
    template_name = 'quizzes/quiz_detail.html'
    context_object_name = 'quiz'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quiz = self.get_object()
        
        # 모든 문제와 해당 선택지 가져오기
        questions = quiz.questions.all().order_by('order')
        context['questions'] = questions
        
        # 현재 사용자가 강사인지 확인
        context['is_instructor'] = self.request.user.is_instructor()
        
        # 현재 사용자가 이 퀴즈를 생성한 강사인지 확인
        context['is_quiz_instructor'] = (self.request.user == quiz.instructor)
        
        # 학생인 경우 이전 시도 정보 가져오기
        if not self.request.user.is_instructor():
            previous_attempts = QuizAttempt.objects.filter(
                quiz=quiz,
                student=self.request.user,
                is_completed=True
            ).order_by('-completed_at')
            
            context['previous_attempts'] = previous_attempts
            context['has_completed'] = previous_attempts.exists()
        
        return context

# 퀴즈 수정 뷰
class QuizUpdateView(LoginRequiredMixin, InstructorRequiredMixin, UpdateView):
    model = Quiz
    form_class = QuizForm
    template_name = 'quizzes/quiz_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # 폼 초기화 시 강의 정보 전달
        kwargs['course'] = self.get_object().course
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_update'] = True
        return context
    
    def get_success_url(self):
        return reverse('quizzes:quiz_detail', kwargs={'pk': self.object.id})
    
    # 강의를 생성한 강사만 수정 가능하도록 추가 검사
    def test_func(self):
        quiz = self.get_object()
        return super().test_func() and self.request.user == quiz.instructor

# 퀴즈 삭제 뷰
class QuizDeleteView(LoginRequiredMixin, InstructorRequiredMixin, DeleteView):
    model = Quiz
    template_name = 'quizzes/quiz_confirm_delete.html'
    
    def get_success_url(self):
        course_id = self.get_object().course.id
        return reverse('quizzes:quiz_list', kwargs={'course_id': course_id})
    
    # 강의를 생성한 강사만 삭제 가능하도록 추가 검사
    def test_func(self):
        quiz = self.get_object()
        return super().test_func() and self.request.user == quiz.instructor
    
# 문제 생성 뷰
class QuestionCreateView(LoginRequiredMixin, InstructorRequiredMixin, CreateView):
    model = Question
    form_class = QuestionForm
    template_name = 'quizzes/question_form.html'
    
    def get_quiz(self):
        quiz_id = self.kwargs.get('quiz_id')
        return get_object_or_404(Quiz, id=quiz_id)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quiz = self.get_quiz()
        context['quiz'] = quiz
        
        # 이미 생성된 문제 수
        existing_questions_count = quiz.questions.count()
        context['existing_questions_count'] = existing_questions_count
        
        if self.request.POST:
            context['choice_formset'] = ChoiceFormSet(self.request.POST)
        else:
            context['choice_formset'] = ChoiceFormSet()
            # 기본 순서 설정
            context['form'].initial = {'order': existing_questions_count + 1}
        
        return context
    
    def form_valid(self, form):
        quiz = self.get_quiz()
        
        # 권한 확인 - 퀴즈 생성자만 문제 추가 가능
        if quiz.instructor != self.request.user:
            messages.error(self.request, '권한이 없습니다.')
            return redirect('quizzes:quiz_detail', pk=quiz.id)
        
        form.instance.quiz = quiz
        
        # 선택지 폼셋 가져오기
        choice_formset = ChoiceFormSet(self.request.POST)
        
        if choice_formset.is_valid():
            with transaction.atomic():
                # 문제 저장
                self.object = form.save()
                
                # 선택지 저장
                choice_formset.instance = self.object
                choice_formset.save()
                
                # 정답이 하나만 선택되었는지 확인
                correct_choices = self.object.choices.filter(is_correct=True)
                if correct_choices.count() != 1:
                    messages.error(self.request, '정답은 하나만 선택해야 합니다.')
                    # 롤백을 위해 예외 발생
                    raise ValidationError('정답은 하나만 선택해야 합니다.')
                
                messages.success(self.request, '문제가 성공적으로 추가되었습니다.')
                
                # 계속 문제 추가 또는 완료할지 결정
                if 'add_another' in self.request.POST:
                    return redirect('quizzes:question_create', quiz_id=quiz.id)
                return redirect('quizzes:quiz_detail', pk=quiz.id)
        else:
            return self.form_invalid(form)
    
    def test_func(self):
        quiz = self.get_quiz()
        return super().test_func() and self.request.user == quiz.instructor

# 문제 수정 뷰
class QuestionUpdateView(LoginRequiredMixin, InstructorRequiredMixin, UpdateView):
    model = Question
    form_class = QuestionForm
    template_name = 'quizzes/question_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question = self.get_object()
        context['quiz'] = question.quiz
        context['is_update'] = True
        
        if self.request.POST:
            context['choice_formset'] = ChoiceFormSet(self.request.POST, instance=question)
        else:
            context['choice_formset'] = ChoiceFormSet(instance=question)
        
        return context
    
    def form_valid(self, form):
        question = self.get_object()
        
        # 권한 확인 - 퀴즈 생성자만 문제 수정 가능
        if question.quiz.instructor != self.request.user:
            messages.error(self.request, '권한이 없습니다.')
            return redirect('quizzes:quiz_detail', pk=question.quiz.id)
        
        # 선택지 폼셋 가져오기
        choice_formset = ChoiceFormSet(self.request.POST, instance=question)
        
        if choice_formset.is_valid():
            with transaction.atomic():
                # 문제 저장
                self.object = form.save()
                
                # 선택지 저장
                choice_formset.save()
                
                # 정답이 하나만 선택되었는지 확인
                correct_choices = self.object.choices.filter(is_correct=True)
                if correct_choices.count() != 1:
                    messages.error(self.request, '정답은 하나만 선택해야 합니다.')
                    # 롤백을 위해 예외 발생
                    from django.core.exceptions import ValidationError
                    raise ValidationError('정답은 하나만 선택해야 합니다.')
                
                messages.success(self.request, '문제가 성공적으로 수정되었습니다.')
                return redirect('quizzes:quiz_detail', pk=question.quiz.id)
        else:
            return self.form_invalid(form)
    
    def test_func(self):
        question = self.get_object()
        return super().test_func() and self.request.user == question.quiz.instructor

# 문제 삭제 뷰
class QuestionDeleteView(LoginRequiredMixin, InstructorRequiredMixin, DeleteView):
    model = Question
    template_name = 'quizzes/question_confirm_delete.html'
    
    def get_success_url(self):
        quiz_id = self.get_object().quiz.id
        return reverse('quizzes:quiz_detail', kwargs={'pk': quiz_id})
    
    def test_func(self):
        question = self.get_object()
        return super().test_func() and self.request.user == question.quiz.instructor