from django import forms
from .models import InstructorApplication


class InstructorApplicationForm(forms.ModelForm):

    class Meta:
        model = InstructorApplication
        fields = ("qualifications", "experience", "sample_video_url")
        widgets = {
            "qualifications": forms.Textarea(
                attrs={"rows": 5, "placeholder": "자격 사항을 입력하세요."}
            ),
            "experience": forms.Textarea(
                attrs={"rows": 5, "placeholder": "경력 사항을 입력하세요."}
            ),
            "sample_video_url": forms.URLInput(
                attrs={"placeholder": "샘플 강의 영상 URL을 입력하세요."}
            ),
        }
