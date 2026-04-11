from django.shortcuts import render, redirect
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

        # Sincroniza o carrinho com o estoque atual
        cart_variation_ids = list(cart.keys())
        db_variations = Variation.objects.select_related('product').filter(id__in=cart_variation_ids)

        error_found = False
        
        for variation in db_variations:
            vid = str(variation.id)
            stock = variation.stock
            cart_item = cart[vid]

            # Busca o preço atualizado no banco de dados
            current_price = float(variation.get_price())

            # Verificação de estoque: se a quantidade no carrinho excede o estoque disponível, ajusta ou remove o item
            if stock < cart_item['qty']:
                error_found = True
                if stock <= 0:
                    # ESTOQUE ZERADO: Remove o item completamente
                    messages.error(self.request, f"O produto '{variation.product.name}' esgotou e foi removido.")
                    del cart[vid]
                else:
                    # ESTOQUE INSUFICIENTE: Apenas baixamos a quantidade para o máximo possível
                    messages.warning(self.request, f"A quantidade de '{variation.product.name}' foi ajustada para {stock}, pois é o limite do nosso estoque.")
                    cart[vid]['qty'] = stock
                    cart[vid]['total_price'] = current_price * stock
            
            # Verifica se o preço do item no carrinho está desatualizado e atualiza se necessário
            elif float(cart_item.get('price', 0)) != current_price:
                cart_item['price'] = current_price
                cart_item['total_price'] = current_price * cart_item['qty']
                messages.info(self.request, f"O preço de '{variation.product.name}' foi atualizado para R${current_price:.2f}.")
                self.request.session.modified = True
              
        if error_found:
            self.request.session.modified = True  # Garante que a sessão seja salva após as alterações
            return redirect('product:cart_detail')

        if not cart or len(cart) == 0:
            messages.warning(self.request, "Seu carrinho ficou vazio após as atualizações. Adicione produtos para finalizar seu pedido.")
            return redirect('product:cart_detail')

        # cart_total_price = sum(float(item['total_price']) for item in cart.values())
        # cart_total_qty = sum(item['qty'] for item in cart.values())
        cart_totals = cart_helper.get_cart_totals(cart, db_variations)

        context = {
            'cart': cart,
            **cart_totals
        }

        return render(self.request, self.template_name, context)