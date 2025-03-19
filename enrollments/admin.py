from django.contrib import admin

from enrollments.models import Enrollment


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    """✅ Django Admin에서 수강 관리 가능하도록 설정"""

    list_display = ("student", "course", "status", "progress", "enrolled_at")  # ✅ 리스트에 표시할 필드
    list_filter = ("status", "course")  # ✅ 필터 기능 추가 (수강 상태, 강의별 필터)
    search_fields = ("student__username", "course__title")  # ✅ 검색 기능 추가 (학생 이름, 강의 제목)
    ordering = ("-enrolled_at",)  # ✅ 최근 수강 등록순 정렬
    list_editable = ("status", "progress")  # ✅ 리스트에서 수강 상태, 진행률 직접 수정 가능
