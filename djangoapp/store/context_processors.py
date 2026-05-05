from cart.service.cart import CartService

def cart_context_processor(request):
    cart_session = CartService.get_cart_instance(request)
    return {
        'cart_total_items': CartService.get_cart_items_count(cart_session)
    }