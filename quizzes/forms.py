# quizzes/forms.py
from django import forms

from courses.models import Lesson, Section

from .models import Answer, Choice, Question, Quiz


class QuizForm(forms.ModelForm):
    """퀴즈 생성/수정 폼"""

    class Meta:
        model = Quiz
        fields = ("title", "description", "section", "lesson")
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'section': forms.Select(attrs={'class': 'form-control'}),
            'lesson': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        course = kwargs.pop('course', None)
        super().__init__(*args, **kwargs)
        
        if course:
            # 해당 강의의 섹션만 선택 가능하도록 제한
            self.fields['section'].queryset = Section.objects.filter(course=course)
            # 해당 강의의 레슨만 선택 가능하도록 제한
            self.fields['lesson'].queryset = Lesson.objects.filter(section__course=course)
            
            # 선택 사항이므로 필수가 아님을 표시
            self.fields['section'].required = False
            self.fields['lesson'].required = False
            
            # 라벨 추가
            self.fields['section'].label = '섹션 (선택사항)'
            self.fields['lesson'].label = '강의 영상 (선택사항)'


class QuestionForm(forms.ModelForm):
    """문제 생성/수정 폼"""

    class Meta:
        model = Question
        fields = ("text", "order")
        widgets = {
            "text": forms.Textarea(attrs={"rows": 3}),
            "order": forms.NumberInput(attrs={"min": 1}),
        }


class ChoiceForm(forms.ModelForm):
    """선택지 생성/수정 폼"""

    class Meta:
        model = Choice
        fields = ("text", "is_correct")
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control'}),
            'is_correct': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


ChoiceFormSet = forms.inlineformset_factory(
    Question,
    Choice,
    form=ChoiceForm,
    extra=5,  # 5지선다
    max_num=5,
    min_num=5,
    validate_min=True,
    validate_max=True,
    can_delete=False,
)


class AnswerForm(forms.ModelForm):
    """답변 제출 폼"""

    class Meta:
        model = Answer
        fields = ("selected_choice",)
        widgets = {
            "selected_choice": forms.RadioSelect(),
        }

    def __init__(self, *args, **kwargs):
        question = kwargs.pop("question", None)
        super().__init__(*args, **kwargs)

        if question:
            # 해당 문제의 선택지만 선택할 수 있도록 제한
            self.fields["selected_choice"].queryset = question.choices.all()
