# quizzes/forms.py
from django import forms

from .models import Answer, Choice, Question, Quiz


class QuizForm(forms.ModelForm):
    """퀴즈 생성/수정 폼"""

    class Meta:
        model = Quiz
        fields = ("title", "description")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }


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
