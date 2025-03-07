from .models import InstructorApplication
from .forms import InstructorApplicationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def instructor_application_view(request):
    """강사 신청 뷰"""
    # 이미 강사인 경우
    if request.user.is_instructor():
        messages.info(request, "이미 강사 권한을 가지고 있습니다.")
        return redirect("accounts:profile")

    # 이미 신청한 경우
    existing_application = InstructorApplication.objects.filter(
        user=request.user, status=InstructorApplication.Status.PENDING
    ).first()

    if existing_application:
        messages.info(
            request, "이미 강사 신청이 진행 중입니다. 관리자의 승인을 기다려주세요."
        )
        return redirect("accounts:profile")

    if request.method == "POST":
        form = InstructorApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.save()
            messages.success(
                request, "강사 신청이 접수되었습니다. 심사 후 결과를 알려드립니다."
            )
            return redirect("accounts:profile")
    else:
        form = InstructorApplicationForm()

    return render(request, "accounts/instructor_application.html", {"form": form})
