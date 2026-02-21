def get_item_quant(cart_session, variation_id):
    """Retorna a quantidade do item no carrinho como inteiro."""
    return int(cart_session.get(str(variation_id), 0))

def get_cart_totals(cart_session, variations):
    """
    Cálculo centralizado para evitar loops múltiplos e chamadas redundantes.
    Retorna um dicionário com todos os valores necessários.
    """
    cart_subtotal = 0
    grand_total = 0

    for variation in variations:
        quantity = get_item_quant(cart_session, variation.id)
        
        # Preço bruto
        cart_subtotal += variation.price * quantity
        
        # Preço efetivo (promoção ou cheio)
        price_eff = variation.promotional_price if variation.promotional_price > 0 else variation.price
        grand_total += price_eff * quantity

    # Cálculo do desconto absoluto 
    total_discount = cart_subtotal - grand_total

    # Cálculo do percentual (com "trava de segurança")
    total_discount_percent = round((total_discount / cart_subtotal) * 100, 2) if cart_subtotal > 0 else 0

    return {
        'cart_subtotal': cart_subtotal,
        'grand_total': grand_total,
        'total_discount': total_discount,
        'total_discount_percent': total_discount_percent,
        'total_items_count': sum(cart_session.values()) if cart_session else 0
    }