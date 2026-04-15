from django.shortcuts import render, redirect
from utils.validator import cart as cart_auth
from django.views import View

from product.models import Variation

from django.contrib import messages
from utils.helper import cart_calculations as cart_helper

class CheckoutSummaryView(View):
    template_name = 'order/order-summary.html'

    def get(self, *args, **kwargs):
        # Proteção de autenticação
        if not self.request.user.is_authenticated:
            messages.warning(self.request, "Faça login para finalizar seu pedido.")
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

        context = {
            'cart': cart,
            **cart_totals
        }

        return render(self.request, self.template_name, context)