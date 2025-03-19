from .models import CartItem


def cart_count(request):
    """✅ 로그인한 사용자의 장바구니 개수 반환"""
    if request.user.is_authenticated:
        return {"cart_count": CartItem.objects.filter(user=request.user).count()}
    return {"cart_count": 0}
