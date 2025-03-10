from django.views.generic import CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect

from .models import InstructorApplication, User
from .forms import InstructorApplicationForm


class InstructorApplicationView(LoginRequiredMixin, CreateView):
    model = InstructorApplication
    form_class = InstructorApplicationForm
    template_name = "accounts/instructor_application.html"
    success_url = reverse_lazy("accounts:profile")

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        if user.is_instructor():
            messages.info(request, "이미 강사 권한을 가지고 있습니다.")
            return redirect("accounts:profile")

        existing_application = InstructorApplication.objects.filter(
            user=self.request.user, status=InstructorApplication.Status.PENDING
        ).first()

        if existing_application:
            messages.info(
                request, "이미 강사 신청이 진행 중입니다. 관리자의 승인을 기다려주세요."
            )
            return redirect("accounts:profile")

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user

        messages.success(
            self.request, "강사 신청이 접수되었습니다. 심사 후 결과를 알려드립니다."
        )

        return super().form_valid(form)


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile.html"
