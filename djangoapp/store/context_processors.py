from utils.helper.cart_calculations import get_cart_items_count

def cart_context_processor(request):
    cart_session = request.session.get('cart', {})
    return {
        'cart_total_items': get_cart_items_count(cart_session)
    }