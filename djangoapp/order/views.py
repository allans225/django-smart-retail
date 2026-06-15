from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.contrib import messages

from utils.mixins import CartValidationMixin
from utils.mixins import MessageMixin
from utils.validator.address import get_user_address

from cart.service.cart import CartService
from order.service.order import OrderService
from django.views import View

class CheckoutSummaryView(LoginRequiredMixin, MessageMixin, CartValidationMixin, View):
    template_name = 'order/order-summary.html'

    def get(self, request):
        address = get_user_address(self.request.user)
        if not address:
            self.render_message(
                self.request, message="Adicione um endereço para finalizar seu pedido.",
                level=messages.WARNING, status=400
            )
            return redirect('account:auth_page')
            # >> TO DO: Redirecionar para a página de gerenciamento de endereços nas configurações do perfil

        # Invoca CartValidationMixin para validar o carrinho e sincronizar os dados, garantindo que o usuário receba feedback imediato sobre qualquer problema (ex: itens indisponíveis, estoque insuficiente, etc.)
        cart, active_variations, redirect_response = self.validate_and_sync_cart(request)

        if redirect_response:
            # Se houver um redirecionamento necessário (ex: carrinho vazio, itens inválidos), retorna imediatamente a resposta de redirecionamento.
            return redirect_response

        variation_dict = {str(v.id): v for v in active_variations}
        # Gera a lista de itens para o template, usando as variações ativas para garantir dados atualizados (preço, nome, imagem, etc.)
        cart_template = cart.get_selected_items_list(variation_dict)
        # Totais levando em consideração apenas os itens selecionados
        totals = CartService.get_full_calculations(cart, active_variations)

        context = {'address': address, 'cart_items': cart_template, **totals}

        return render(self.request, self.template_name, context)
   
class CreateOrderView(LoginRequiredMixin, MessageMixin, CartValidationMixin, View):
    def post(self, request):
        address = get_user_address(self.request.user)
        if not address:
            self.render_message(
                self.request,
                message="Adicione um endereço para finalizar seu pedido.",
                level=messages.WARNING
            )
            # >> TO DO: Redirecionar para a página de gerenciamento de endereços nas configurações do perfil
            return redirect('account:auth_page')

        cart, active_variations, redirect_response = self.validate_and_sync_cart(request)
        if redirect_response:
            return redirect_response
        
        cart_totals = CartService.get_full_calculations(cart, active_variations)

        try:
            # Criar o pedido, os itens do pedido, e atualizar o estoque dentro da transação atômica, garantindo a integridade dos dados
            OrderService.create_order(request.user, cart, cart_totals, active_variations)
            cart.remove_selected_items() # Método para remover apenas os itens selecionados do carrinho, mantendo itens não selecionados intactos
            CartService.save(request, cart) # Salva o estado atualizado do carrinho
            # Sucesso: 
            self.render_message(self.request, message="Pedido realizado com sucesso!", level=messages.SUCCESS)
            return redirect('product:all') # >>> TO DO: Redirecionar para a página de pedidos no menu do usuário
        
        except ValueError as ve: # Captura erros de negócio relacionado ao Service
            self.render_message(self.request, message=str(ve), level=messages.WARNING)
            return redirect('order:checkout_summary')

        except Exception as e:
            self.render_message(self.request, message=f"Erro ao processar pedido: {str(e)}", level=messages.ERROR)
            return redirect('order:checkout_summary')