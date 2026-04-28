from decimal import Decimal

def validate_and_sync_cart(cart, db_variations):
    """
    Responsável por sincronizar os dados na interface do usuário com o banco de dados
    """
    notifications = []
    has_changes = False

    # Dicionário para acesso rápido às variações
    variations_dict = {str(v.id): v for v in db_variations}

    # Cast para list para permitir deletar itens durante a iteração
    for vid, data in list(cart.items()):
        variation = variations_dict.get(vid)
        print(data) 
        
        # Se a variação não existe no DB
        if not variation:
            # Pegamos o nome que já estava no carrinho para notificar
            product_name = data.get('product_name', 'Produto indisponível')
            notifications.append({
                'type': 'error', 
                'message': f"{product_name} não está mais disponível e foi removido."
            })
            del cart[vid]
            has_changes = True
            continue # Pula para o próximo item
        
        item_qty = data.get('qty', 0) # Quantidade da variação do produto no carrinho (que o usuário deseja comprar)

        # Buscando a quantidade e preço atualizados da variação do produto
        item_stock = variation.stock
        # Variável auxiliar para controlar se este item específico mudou
        item_changed = False

        # Verificação de estoque
        if item_stock < item_qty:
            has_changes = True
            item_changed = True
            if item_stock <= 0:
                # ESTOQUE ZERADO: Remove o item completamente
                notifications.append({
                    'type': 'error',
                    'message': f"O produto '{variation.product.name}' esgotou e foi removido."
                })
                del cart[vid]
                continue # item removido, não precisa checar preço
            else:
                # ESTOQUE INSUFICIENTE: Apenas diminui a quantidade para o máximo possível
                notifications.append({
                    'type': 'warning', 
                    'message': f"A quantidade de '{variation.product.name}' foi ajustada para {item_stock}."
                })
                cart[vid]['qty'] = item_stock
                item_qty = item_stock # Atualiza variável local para o cálculo do total_price no final do loop

        # Garante que o preço seja tratado como Decimal para evitar problemas de precisão
        current_price = Decimal(str(variation.get_price()))
        # O preço do item no carrinho (cast para Decimal para comparação precisa)
        session_price = Decimal(str(data.get('price', 0)))
        print(f"Session: {session_price} | DB: {current_price}")
        # Verifica se o preço do item no carrinho está desatualizado
        if session_price != current_price:
            has_changes = True
            item_changed = True
            # armazenar como float na sessão (JSON friendly)
            cart[vid]['price'] = float(current_price)
            notifications.append({
                'type': 'info', 
                'message': f"O preço de '{variation.product.name}' foi atualizado para R${current_price:.2f}."
            })

        # Se houve qualquer mudança no item (estoque ou preço), atualiza o total do item no carrinho
        if item_changed:
            total_price = current_price * Decimal(str(item_qty))
            cart[vid]['total_price'] = float(total_price) # Armazena como float para JSON
            cart[vid]['price'] = float(current_price) # Garante que o preço atualizado também seja salvo
    
    return cart, notifications, has_changes