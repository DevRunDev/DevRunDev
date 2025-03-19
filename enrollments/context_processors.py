def cart_count(request):
    """장바구니에 담긴 강의 개수를 반환"""
    cart = request.session.get("cart", [])
    return {"cart_count": len(cart)}
