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
        price = Decimal(str(data.get('price', '0.00'))) if isinstance(data, dict) else Decimal('0.00')
        total_price = Decimal(str(data.get('total_price', '0.00'))) if isinstance(data, dict) else Decimal('0.00')
        product_name = data.get('product_name', '') if isinstance(data, dict) else ''
        variation_name = data.get('variation_name', '') if isinstance(data, dict) else ''

        return qty, selected, price, total_price, product_name, variation_name

    @classmethod
    def get_cart_items_count(cls, cart_entity):
        """Retorna a quantidade total de itens no carrinho."""
        if not cart_entity or not cart_entity.items:
            return 0
        # Somamos as quantidades de cada item, garantindo que sejam dicionários válidos com a chave 'qty'.
        return sum(cls.data_normalization(data)[0] for data in cart_entity.items.values())

    @classmethod
    def get_full_calculations(cls, cart_entity, db_variations):
        """Cálculo centralizado para evitar loops múltiplos e chamadas redundantes. Retorna um dicionário com todos os valores necessários."""
        items_dict = {str(item.id): item for item in db_variations}

        totals = {
            'selected_items_count': 0,
            'total_items_count': 0,
            'cart_subtotal': Decimal('0.00'),
            'grand_total': Decimal('0.00'),
        }

        for variation_id, data in cart_entity.items.items():
            item = items_dict.get(str(variation_id))
            if not item: continue

            qty, selected, _, _, _, _ = cls.data_normalization(data)

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

    @classmethod
    def sync_cart(cls, cart_entity, db_variations):
        db_items_dict = {str(v.id): v for v in db_variations}
        cart = cart_entity.items
        changes = [] # lista para capturar mudanças e informar o usuário posteriormente

        # Para cada item no carrinho, verificamos se ele ainda existe no banco de dados e se os dados estão atualizados.
        for id, data in list(cart.items()):
            db_item = db_items_dict.get(str(id))
            if not db_item: # Se o item não existe mais ou está esgotado, removemos do carrinho e notificamos o usuário.
                product_name_del = cart[id].get('product_name', 'Produto') if isinstance(cart[id], dict) else 'Produto'
                changes.append(f"O produto '{product_name_del}' não está mais disponível e foi removido do seu carrinho.")
                del cart[id]
                continue
            
            # Normalizando dados do item do carrinho para comparação e atualização
            item_qty, _, _, _, product_name, variation_name = cls.data_normalization(data)

            # Atualizamos os nomes do produto e variação para garantir que estejam sempre sincronizados com o banco de dados.
            cart[id]['product_name'] = db_item.product.name if product_name != db_item.product.name else product_name
            cart[id]['variation_name'] = db_item.name if variation_name != db_item.name else variation_name

            # Verificação de estoque: Se a quantidade no carrinho for maior que o estoque disponível, 
            # ajustamos para o máximo possível ou removemos se estiver esgotado.
            if db_item.stock < item_qty:
                if db_item.stock <= 0:
                    changes.append(f"O produto '{db_item.product.name} - {db_item.name}' está esgotado e foi removido do seu carrinho.")
                    del cart[id]
                    continue
                else:
                    cart[id]['qty'] = db_item.stock
                    changes.append(f"A quantidade do produto '{db_item.product.name} - {db_item.name}' foi ajustada para {db_item.stock} devido à disponibilidade em estoque.")

            current_price = Decimal(str(db_item.get_price())) # Preço atualizado do item no banco de dados (com desconto aplicado, se houver)
            session_price = Decimal(str(data.get('price', '0.00'))) # Preço do item no carrinho (sessão)

            # Se o preço do item no carrinho estiver desatualizado em relação ao banco de dados, 
            # atualizamos para garantir que o usuário veja o valor correto.
            if current_price != session_price:
                cart[id]['price'] = float(current_price)
                price_fmt = f"R${current_price:.2f}".replace('.', ',')
                changes.append(f"O preço do produto '{db_item.product.name} - {db_item.name}' foi atualizado para {price_fmt}.")
            
        return cart_entity, changes