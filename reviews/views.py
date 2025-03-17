from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from courses.models import Course

from .forms import ReviewForm
from .models import Review


class ReviewCreateView(View):
    """강의 리뷰 작성 뷰"""

    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)

        # ✅ 강사가 리뷰를 작성할 수 없도록 제한
        if request.user.is_instructor():
            messages.error(request, "강사는 리뷰를 남길 수 없습니다.")
            return redirect("courses:course_detail", course_id)

        # ✅ 이미 리뷰를 작성한 경우 제한
        if Review.objects.filter(course=course, user=request.user).exists():
            messages.error(request, "이미 이 강의에 대한 리뷰를 작성하셨습니다.")
            return redirect("courses:course_detail", course_id)

        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.course = course
            review.user = request.user
            review.save()
            messages.success(request, "리뷰가 등록되었습니다.")
        return redirect("courses:course_detail", course_id)


class ReviewUpdateView(View):
    """강의 리뷰 수정 뷰"""

    def post(self, request, review_id):
        review = get_object_or_404(Review, id=review_id, user=request.user)
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "리뷰가 수정되었습니다.")
        return redirect("courses:course_detail", review.course.id)


class ReviewDeleteView(View):
    """강의 리뷰 삭제 뷰"""

    def post(self, request, review_id):
        review = get_object_or_404(Review, id=review_id, user=request.user)
        course_id = review.course.id
        review.delete()
        messages.success(request, "리뷰가 삭제되었습니다.")
        return redirect("courses:course_detail", course_id)
