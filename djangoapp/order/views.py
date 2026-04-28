from django.shortcuts import render, redirect
from utils.validator import cart as cart_auth
from django.db import transaction

from django.views import View
from product.models import Variation, VariationImage
from order.models import Order, OrderItem
from utils.validator.address import get_user_address

from django.contrib import messages
from utils.helper import cart_calculations as cart_helper

class CheckoutSummaryView(View):
    template_name = 'order/order-summary.html'

    def get(self, *args, **kwargs):
        # Proteção de autenticação
        if not self.request.user.is_authenticated:
            messages.warning(self.request, "Faça login para finalizar seu pedido.")
            return redirect('account:auth_page')
        
        address = get_user_address(self.request.user)

        if not address:
            messages.warning(self.request, "Adicione um endereço para finalizar seu pedido.")
            # >> TO DO: Redirecionar para a página de gerenciamento de endereços nas configurações do perfil
            return redirect('account:auth_page')

        cart = self.request.session.get('cart')

        # Proteção contra acesso direto sem itens no carrinho
        if not cart:
            messages.warning(self.request, "Seu carrinho está vazio.")
            return redirect('product:cart_detail')

        cart_variation_ids = list(cart.keys())
        db_variations = Variation.objects.select_related('product').filter(id__in=cart_variation_ids)

        # Sincroniza o carrinho com o estoque atual
        cart, notifications, has_changed = cart_auth.validate_and_sync_cart(cart, db_variations)
            
        if notifications:
            for note in notifications:
                if note['type'] == 'error':
                    messages.error(self.request, note['message'])
                elif note['type'] == 'warning':
                    messages.warning(self.request, note['message'])
                elif note['type'] == 'info':
                    messages.info(self.request, note['message'])

        if has_changed:
            self.request.session.modified = True  # Garante que a sessão seja salva após as alterações
            return redirect('product:cart_detail')

        if not cart or len(cart) == 0:
            messages.warning(self.request, "Seu carrinho ficou vazio após as atualizações. Adicione produtos para finalizar seu pedido.")
            return redirect('product:cart_detail')

        cart_totals = cart_helper.get_cart_totals(cart, db_variations)

        # Convertendo o carrinho para uma lista de itens detalhados para renderização no template
        variations_dict = {str(v.id): v for v in db_variations}
        cart_items_template = []
        for vid, data in cart.items():
            variation = variations_dict.get(str(vid))
            if variation:
                cart_items_template.append({
                    'variation': variation,
                    'quantity': data.get('qty', 0),
                    'price': data.get('price', 0),
                    'total_price': data.get('qty', 0) * data.get('price', 0),
                })

        context = {
            'address': address,
            'cart': cart,
            'cart_items': cart_items_template,
            **cart_totals
        }

        return render(self.request, self.template_name, context)
    
class CreateOrderView(View):
    def post(self, request, *args, **kwargs):
        # proteção de autenticação
        if not self.request.user.is_authenticated:
            messages.warning(self.request, "Faça login para finalizar seu pedido.")
            return redirect('account:auth_page')
        
        address = get_user_address(self.request.user)
        if not address:
            messages.warning(self.request, "Adicione um endereço para finalizar seu pedido.")
            # >> TO DO: Redirecionar para a página de gerenciamento de endereços nas configurações do perfil
            return redirect('account:auth_page')
        
        cart = self.request.session.get('cart')
        if not cart:
            messages.warning(self.request, "Seu carrinho está vazio.")
            return redirect('product:cart_detail')
        
        # buscando as variações para garantir o preço, estoque atual e as imagens relacionadas 
        # (related_name='images' -> VariationImage.variation)
        cart_variation_ids = list(cart.keys())
        db_variations = Variation.objects.select_related('product') \
            .prefetch_related('images') \
            .filter(id__in=cart_variation_ids) \

        # Recalculando tudo no servidor, garantindo integridade dos dados
        cart_totals = cart_helper.get_cart_totals(cart, db_variations)

        # Criando o pedido e itens do pedido
        try:
            # garantir que salve tudo, ou nada, evitando pedidos incompletos
            with transaction.atomic():
                order = Order.objects.create(
                    user=self.request.user,
                    total=cart_totals['grand_total'],
                    total_items=cart_totals['total_items_count'],
                    status='C'  # Criado
                )

                order.save()  # Salva o pedido para gerar o ID necessário para os itens

                variations_dict = {str(v.id): v for v in db_variations}
                for vid, data in cart.items():
                    # Recupera o objeto Variation do dicionário usando o ID (vid) da sessão.
                    # Usar um dicionário em memória evita consultas repetitivas ao banco de dados dentro do loop.
                    variation = variations_dict.get(str(vid))
                    if not variation:
                        product_name = data.get('product_name', 'Produto indisponível')
                        raise Exception(f"O produto {product_name} não está mais disponível.")
                
                    qty_requested = data.get('qty', 0)

                    if variation.stock < qty_requested:
                        raise Exception(
                            f"Estoque insuficiente para {variation.product.name} - {variation.name}. Disponível: {variation.stock}, Solicitado: {qty_requested}"
                        )

                    # Tenta obter a imagem da variação
                    variation_img_obj = variation.images.first()
                    if variation_img_obj and variation_img_obj.image:
                        img_path = variation_img_obj.image.url
                    # Senão, tenta obter a imagem de capa do produto base
                    elif variation.product.cover_image:
                        img_path = variation.product.cover_image.url
                    else:
                        img_path = ""
                    
                    OrderItem.objects.create(
                        order=order,
                        product_name=variation.product.name,
                        product_id=variation.product.id,
                        variation_name=variation.name,
                        variation_id=variation.id,
                        price=variation.price,
                        promotional_price=variation.promotional_price,
                        quantity=qty_requested,
                        image=img_path
                    )

                    # Atualiza o estoque da variação
                    variation.stock -= qty_requested
                    variation.save()

                # Limpa o carrinho após criar os itens do pedido
                del request.session['cart']
                request.session.modified = True

            # Sucesso total
            messages.success(request, "Pedido realizado com sucesso!")
            return redirect('product:all') # >>> TO DO: Redirecionar para a página de pedidos no menu do usuário

        except Exception as e:
            messages.error(self.request, f"Erro ao processar pedido: {str(e)}")
            return redirect('order:checkout_summary')