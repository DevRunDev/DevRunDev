from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):
    """리뷰 작성 폼"""

    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.Select(choices=Review.RATING_CHOICES, attrs={"class": "form-select"}),
            "comment": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
