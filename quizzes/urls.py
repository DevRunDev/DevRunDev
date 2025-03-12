# quizzes/urls.py
from django.urls import path

from . import views

app_name = 'quizzes'

urlpatterns = [
    # 퀴즈 목록 및 생성
    path('course/<int:course_id>/quizzes/', views.QuizListView.as_view(), name='quiz_list'),
    path('course/<int:course_id>/quizzes/create/', views.QuizCreateView.as_view(), name='quiz_create'),
    
    # 퀴즈 상세, 수정, 삭제
    path('<int:pk>/', views.QuizDetailView.as_view(), name='quiz_detail'),
    path('<int:pk>/edit/', views.QuizUpdateView.as_view(), name='quiz_edit'),
    path('<int:pk>/delete/', views.QuizDeleteView.as_view(), name='quiz_delete'),
    
    # 문제 관리
    path('quizzes/<int:quiz_id>/questions/create/', views.QuestionCreateView.as_view(), name='question_create'),
    path('questions/<int:pk>/edit/', views.QuestionUpdateView.as_view(), name='question_edit'),
    path('questions/<int:pk>/delete/', views.QuestionDeleteView.as_view(), name='question_delete'),
    

]