def get_cart_items_count(cart_session):
    """Retorna a quantidade total de itens no carrinho."""
    if not cart_session:
        return 0
    # Somamos as quantidades de cada item, garantindo que sejam dicionários válidos com a chave 'qty'.
    return sum(item['qty'] for item in cart_session.values() if isinstance(item, dict) and 'qty' in item)

def get_item_quant(cart_session, variation_id):
    """Retorna a quantidade do item no carrinho como inteiro."""
    # Garante que o valor retornado seja int e que o acesso ao dicionário seja seguro."
    return int(cart_session.get(str(variation_id), {}).get('qty', 0)) if cart_session else 0

def get_cart_totals(cart_session, variations_queryset):
    """
    Cálculo centralizado para evitar loops múltiplos e chamadas redundantes.
    Retorna um dicionário com todos os valores necessários.
    """
    # Criamos um dicionário para acesso rápido às variações, evitando loops aninhados
    variations_dict = {str(v.id): v for v in variations_queryset} # v.id => variation_id
    total_items_count = 0
    cart_subtotal = 0
    grand_total = 0

    for variation_id, data in cart_session.items():
        variation = variations_dict.get(str(variation_id))
        if not variation:
            continue  # Ignora itens que não correspondem a variações válidas

        # Extração segura
        if isinstance(data, dict):
            is_selected = data.get('selected', True) # Assume selecionado por padrão
            item_qty = data.get('qty', 0)
        else:
            is_selected = True
            item_qty = int(data) if str(data).isdigit() else 0

        # Soma todos os itens da sessão para a badge, selecionados ou não
        total_items_count += item_qty

        # Lógica central para calcular preços se o item estiver selecionado
        if is_selected and item_qty > 0:
            price = float(variation.get_price()) # Preço com desconto aplicado, se houver
            base_price = float(variation.price)  # Preço cheio para cálculo de desconto

            cart_subtotal += base_price * item_qty
            grand_total += price * item_qty

    discount_value = cart_subtotal - grand_total
    discount_percent =round((discount_value / cart_subtotal) * 100, 2) if cart_subtotal > 0 else 0

    return {
        'cart_subtotal': cart_subtotal,
        'grand_total': grand_total,
        'total_discount': discount_value,   
        'total_discount_percent': discount_percent,
        'total_items_count': get_cart_items_count(cart_session),
    }