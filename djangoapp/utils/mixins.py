from django.contrib import messages as django_messages
from django.http import JsonResponse
from django.shortcuts import redirect

from cart.service.cart import CartService
from product.models import Variation

class MessageMixin:
    """ 
    Mixin para padronizar notificações em Views.
    Suporte: requisições AJAX (JSON) e tradicionais (Django messages framework).
    """
    def render_message(self, request, message=None, level=django_messages.SUCCESS, extra_data=None, status=200):
        # Obtém a tag amigável para o nível de mensagem (success, error, warning, info)
        tag = django_messages.DEFAULT_TAGS.get(level, 'info')

        # Lógica para req AJAX
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            data = {
                'status': 'success' if status < 400 else 'error',
                'message': message,
                'tags': tag,
            }
            if extra_data:
                data.update(extra_data) # Permite adicionar dados extras como totais atualizados, contagem de itens, etc.
            return JsonResponse(data, status=status)
        
        # Lógica para req tradicional
        django_messages.add_message(request, level, message)
        return None  # A View deve lidar com o redirecionamento

class CartValidationMixin:
    """ 
    Validação, sincronização e retornar o estado atualizado do carrinho
    antes de operações críticas como checkout, garantindo que o usuário 
    receba feedback imediato sobre qualquer problema.
    """
    def validate_and_sync_cart(self, request):
        cart = CartService.get_cart_instance(request)
        if not cart:
            self.render_message(
                request,
                message="Seu carrinho está vazio.",
                level=django_messages.WARNING,
                status=400
            )
            return None, None, redirect('product:all')
        
        selected_item_ids = cart.get_selected_item_ids() # Obtém os IDs dos itens selecionados para checkout
        if not selected_item_ids:
            self.render_message(
                request,
                message="Selecione ao menos um item no carrinho",
                level=django_messages.WARNING,
                status=400
            )
            return None, None, redirect('product:cart_detail')
        
        # Sincroniza o carrinho, garantindo que os itens selecionados ainda sejam válidos (existam no banco e tenham estoque), e captura notificações para o usuário caso haja mudanças.
        db_variations = Variation.objects.select_related('product').filter(id__in=cart.items.keys())
        cart, notifications = CartService.sync_cart(cart, db_variations)
        CartService.save(request, cart)

        if notifications:
            for msg in notifications:
                self.render_message(request, message=msg, level=django_messages.WARNING, status=400)

        valid_selected_ids = cart.get_selected_item_ids()
        if not valid_selected_ids:
            self.render_message(
                request,
                message="Não há itens selecionados disponíveis para finalizar o pedido. Verifique o estoque dos seus produtos.",
                level=django_messages.WARNING,
                status=400
            )
            return None, None, redirect('product:cart_detail')
        
        # Filtrar o QuerySet em memória, evitando mais chamadas ao banco, e garantindo que só os itens válidos sejam processados no checkout.
        active_variations = [v for v in db_variations if str(v.id) in valid_selected_ids]

        # Retorna: carrinho atualizado, variações ativas, redirect HTTP ou None
        return cart, active_variations, None
    