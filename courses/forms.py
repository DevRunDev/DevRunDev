from django import forms

from .models import Course


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["title", "description", "price", "status"]
        widgets = {
            "description": forms.Textarea(
                attrs={
                    "rows": 4,
                    "cols": 40,
                    "placeholder": "강의에 대한 설명을 입력하세요.",
                }
            ),
            "price": forms.NumberInput(attrs={"min": 0, "placeholder": "강의 가격 입력 (0이면 무료)"}),
            "status": forms.Select(choices=Course.STATUS_CHOICES),
        }

    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price < 0:
            raise forms.ValidationError("가격은 0 이상이어야 합니다.")
        return price
