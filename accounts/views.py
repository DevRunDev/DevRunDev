from allauth.account.views import SignupView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from .forms import InstructorApplicationForm
from .models import InstructorApplication


class InstructorApplicationView(LoginRequiredMixin, CreateView):
    model = InstructorApplication
    form_class = InstructorApplicationForm
    template_name = "account/instructor_application.html"
    success_url = reverse_lazy("accounts:profile")

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        if user.is_instructor():
            messages.info(request, "이미 강사 권한을 가지고 있습니다.")
            return redirect("account:profile")

        existing_application = InstructorApplication.objects.filter(
            user=self.request.user, status=InstructorApplication.Status.PENDING
        ).first()

        if existing_application:
            messages.info(request, "이미 강사 신청이 진행 중입니다. 관리자의 승인을 기다려주세요.")
            return redirect("account:profile")

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user

        messages.success(self.request, "강사 신청이 접수되었습니다. 심사 후 결과를 알려드립니다.")

        return super().form_valid(form)


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "account/profile.html"


class CustomSignupView(SignupView):
    """회원가입 커스텀 뷰"""

    def form_valid(self, form):
        # 기본 form_valid 메서드 호출하여 사용자 생성
        super().form_valid(form)

        # 성공 메시지 추가
        messages.success(self.request, "회원가입이 완료되었습니다. 로그인하여 서비스를 이용해주세요.")

        # 로그인 페이지로 리다이렉트
        return redirect("account_login")
