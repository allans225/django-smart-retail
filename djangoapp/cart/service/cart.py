from cart.entity.cart import Cart
from product.models import Variation
from decimal import Decimal

class CartService:
    @staticmethod
    def get_cart_instance(request):
        """Instancia a classe Cart a partir da sessão do usuário."""
        return Cart(request.session.get('cart', {}))
    
    @staticmethod
    def save(request, cart):
        """Salva o estado do carrinho na sessão do usuário."""
        request.session['cart'] = cart.to_dict()
        request.session.modified = True

    @staticmethod
    def data_normalization(data):
        """Normaliza os dados do item do carrinho, garantindo que sejam extraídos de forma segura e consistente."""
        qty = data['qty'] if isinstance(data, dict) else int(data)
        selected = data.get('selected', True) if isinstance(data, dict) else True
        return qty, selected

    @classmethod
    def get_cart_items_count(cls, cart_entity):
        """Retorna a quantidade total de itens no carrinho."""
        if not cart_entity or not cart_entity.items:
            return 0
        # Somamos as quantidades de cada item, garantindo que sejam dicionários válidos com a chave 'qty'.
        return sum(cls.data_normalization(data)[0] for data in cart_entity.items.values())

    @classmethod
    def get_full_calculations(cls, cart_entity, items_queryset):
        """Cálculo centralizado para evitar loops múltiplos e chamadas redundantes. Retorna um dicionário com todos os valores necessários."""
        items_dict = {str(item.id): item for item in items_queryset}

        totals = {
            'selected_items_count': 0,
            'total_items_count': 0,
            'cart_subtotal': Decimal('0.00'),
            'grand_total': Decimal('0.00'),
        }

        for variation_id, data in cart_entity.items.items():
            item = items_dict.get(str(variation_id))
            if not item: continue

            qty, selected = cls.data_normalization(data)

            totals['total_items_count'] += qty # Soma todos os itens da sessão para a badge, selecionados ou não

            # Lógica central para calcular preços se o item estiver selecionado
            if selected and qty > 0:
                price = Decimal(item.get_price()) # Preço com desconto aplicado, se houver 
                base_price = Decimal(item.price)  # Preço cheio para cálculo de desconto

                totals['cart_subtotal'] += base_price * qty
                totals['grand_total'] += price * qty
                totals['selected_items_count'] += qty

        discount_value = totals['cart_subtotal'] - totals['grand_total']
        discount_percent = round((discount_value / totals['cart_subtotal']) * 100, 2) if totals['cart_subtotal'] > 0 else Decimal('0.00')

        return {
            'cart_subtotal': float(totals['cart_subtotal']),
            'grand_total': float(totals['grand_total']),
            'selected_items_count': totals['selected_items_count'],
            'total_discount': float(discount_value),
            'total_discount_percent': float(discount_percent),
            'total_items_count': totals['total_items_count'],
        }
    
    @classmethod
    def update_selection_by_scope(cls, cart_entity, scope, is_selected, item_id=None):
        """ Coordena qual estratégia de seleção aplicar baseada no escopo """
        if scope == 'all':
            # Seleciona ou desseleciona todos os itens do carrinho
            cart_entity.toggle_selection(is_selected=is_selected)
        elif scope == 'single':
            # Altera o estado de seleção de um item específico
            cart_entity.toggle_selection(item_id=item_id, is_selected=is_selected)
        elif scope == 'discounted':
            items_ids = cart_entity.items.keys() # Ids das variações presentes no carrinho (sessão)
            items_db = Variation.objects.filter(id__in=items_ids) # Consulta as variações (database)

            discounted_ids = [
                str(i.id) for i in items_db # Filtrando itens com preço promocional válido
                if i.promotional_price > 0 and i.promotional_price < i.price
            ]

            for i_id in cart_entity.items:
                is_promo = i_id in discounted_ids # is_promo é true se a variação for promocional, false caso contrário
                if is_selected:
                    # Modo Foco: Seleciona promoções, desseleciona o restante
                    new_state = True if is_promo else False
                else:
                    # Modo Limpeza: Desmarca apenas o que é promoção, mantém o resto
                    current_state = cart_entity.items[i_id].get('selected', False) if isinstance(cart_entity.items[i_id], dict) else True
                    new_state = False if is_promo else current_state

                cart_entity.toggle_selection(item_id=i_id, is_selected=new_state)
