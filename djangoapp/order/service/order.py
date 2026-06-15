from django.db import transaction
from order.models import Order, OrderItem

class OrderService:
    @classmethod
    def _instantiate_order(cls, user, cart_totals):
        order = Order.objects.create(
            user=user,
            total=cart_totals['grand_total'],
            total_items=cart_totals['selected_items_count'],
            status='C' # Criado
        )
        return order

    @classmethod
    def _instantiate_order_item(cls, order, variation, data):
        # Tenta obter a imagem da variação ou da capa do produto
        first_img = variation.images.first()
        img_path = first_img.image.url if first_img else (
            variation.product.cover_image.url if variation.product.cover_image else ""
        )

        order_item = OrderItem.objects.create(
            order=order,
            product_name=variation.product.name,
            product_id=variation.product.id,
            variation_name=variation.name,
            variation_id=variation.id,
            price=variation.price,
            promotional_price=variation.promotional_price,
            quantity=data.get('qty', 0),
            image=img_path
        )
        return order_item
    
    @classmethod
    def create_order(cls, user, cart_entity, cart_totals, active_variations):
        selected_ids = cart_entity.get_selected_item_ids() # acesso direto aos IDs das variações selecionadas
        variations_dict = {str(v.id): v for v in active_variations} # acesso aos dados das variações em memória

        with transaction.atomic():
            order = cls._instantiate_order(user, cart_totals) # Cria o pedido simples

            # Cria os OrderItems do Order, associa-os ao Order, e atualiza o estoque
            for vid in selected_ids:
                data = cart_entity.items.get(str(vid))
                variation = variations_dict.get(str(vid))

                if not variation:
                    product_name = data.get('product_name', 'Produto indisponível')
                    raise ValueError(f"O produto {product_name} não está mais disponível.")
                
                qty_requested = data.get('qty', 0)
                if variation.stock < qty_requested:
                    raise ValueError(
                        f"Estoque insuficiente para {variation.product.name} - {variation.name}. Disponível: {variation.stock}, Solicitado: {qty_requested}"
                    )
                
                cls._instantiate_order_item(order, variation, data)

                variation.stock -= qty_requested
                variation.save()
        return order