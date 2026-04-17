from django.shortcuts import render, redirect
from utils.validator import cart as cart_auth
from django.views import View

from product.models import Variation
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