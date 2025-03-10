import re

from django import forms

from .models import Course, Lesson, Section


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["title", "description", "price"]
        widgets = {
            "description": forms.Textarea(
                attrs={
                    "rows": 4,
                    "cols": 40,
                    "placeholder": "강의에 대한 설명을 입력하세요.",
                }
            ),
            "price": forms.NumberInput(attrs={"min": 0, "placeholder": "강의 가격 입력 (0이면 무료)"}),
        }

    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price < 0:
            raise forms.ValidationError("가격은 0 이상이어야 합니다.")
        return price


class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ["title"]


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ["title", "video_url"]

    def clean_video_url(self):
        url = self.cleaned_data.get("video_url")
        if not url:
            raise forms.ValidationError("강의에는 동영상이 필수입니다.")

        youtube_regex = (
            r"(https?://)?(www\.)?"
            r"(youtube|youtu|youtube-nocookie)\.(com|be)/"
            r"(watch\?v=|embed/|v/|shorts/|v/|.+\?v=)?([^&=%\?]{11})"
        )
        match = re.search(youtube_regex, url)

        if not match:
            raise forms.ValidationError("유효한 유튜브 URL을 입력해주세요.")

        video_id = match.group(6)
        embed_url = f"https://www.youtube.com/embed/{video_id}"

        # ✅ 변환된 URL을 저장
        self.cleaned_data["video_url"] = embed_url
        return embed_url
