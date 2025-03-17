from django.urls import path

from .views import ReviewCreateView, ReviewDeleteView, ReviewUpdateView

app_name = "reviews"

urlpatterns = [
    path("course/<int:course_id>/add/", ReviewCreateView.as_view(), name="review_add"),
    path("review/<int:review_id>/edit/", ReviewUpdateView.as_view(), name="review_edit"),
    path("review/<int:review_id>/delete/", ReviewDeleteView.as_view(), name="review_delete"),
]
