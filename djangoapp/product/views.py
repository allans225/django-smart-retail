from django.contrib.messages import constants as django_messages
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views import View
from utils.mixins import MessageMixin
from cart.service.cart import CartService
from . import models

class ProductListView(ListView):
    model = models.Product
    template_name = 'product/list.html'
    context_object_name = 'products'
    paginate_by = 20

    def get_queryset(self):
        queryset = models.Product.objects.all()
        return queryset

class DetailProduct(DetailView):
    model = models.Product
    template_name = 'product/detail.html'
    context_object_name = 'product'
    slug_url_kwarg = 'slug'
    
class CartDetailView(View):
    def get(self, request, *args, **kwargs):
        cart = CartService.get_cart_instance(request)
        variation_ids = cart.items.keys()
        variations = models.Variation.objects.filter(
            id__in=variation_ids
        ).select_related('product').order_by('product__name')  # Ordena por nome do produto para exibição mais amigável
        
        cart_items = []
        for variation in variations:
            quantity, is_selected, _, _, _, _ = CartService.data_normalization(cart.items.get(str(variation.id), {}))
            cart_items.append({
                'variation': variation,
                'quantity': quantity,
                'selected': is_selected,  # Adiciona o estado de seleção ao contexto do item
            })

        totals = CartService.get_full_calculations(cart, variations)

        context = {
            'cart_items': cart_items,
            **totals 
        }
        return render(request, 'product/cart.html', context)

class AddToCartView(View, MessageMixin):
    def post(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') != 'XMLHttpRequest':
            return self.render_message(
                request,
                message='Acesso negado',
                level=django_messages.ERROR,
                status=400
            )

        # Garante que o ID seja tratado como String para a Sessão
        variation_id = request.POST.get('variation_id')
        if not variation_id:
            return self.render_message(
                request,
                message='ID da variação ausente',
                level=django_messages.ERROR,
                status=400
            )

        # Validação de quantidade requerida    
        try:
            quantity = int(request.POST.get('quantity', 1))
        except (ValueError, TypeError):
            quantity = 1

        variation = get_object_or_404(models.Variation, id=variation_id)

        # Validação de estoque
        if variation.stock < quantity:
            return self.render_message(
                request,
                message=f'Estoque insuficiente ({variation.stock} disponíveis).',
                level=django_messages.ERROR,
                extra_data={'available_stock': variation.stock},
                status=400
            )

        cart = CartService.get_cart_instance(request) # Instancia Classe Cart a partir da sessão
        cart.add_or_update_item(quantity, variation)  # Add ou atualiza o item no carrinho

        CartService.save(request, cart) # Salvando o carrinho atualizado na sessão

        # Calcular os totais atualizados para retornar na resposta AJAX
        variations = models.Variation.objects.filter(id__in=cart.items.keys())
        full_data = CartService.get_full_calculations(cart, variations)

        return self.render_message(
            request,
            message=f'Adicionado: {variation.product.name} ({variation.name})',
            level=django_messages.SUCCESS,
            extra_data={'total_items_count': full_data['total_items_count']},
            status=200
        )

class RemoveFromCartView(View, MessageMixin):
    def post(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') != 'XMLHttpRequest':
            return self.render_message(
                request,
                message='Acesso negado',
                level=django_messages.ERROR,
                status=400
            )

        variation_id = request.POST.get('variation_id')
        
        # se não houver ID ou se o ID for a string 'null'
        if not variation_id or variation_id == 'null':
            return self.render_message(
                request,
                message='ID da variação inválido',
                level=django_messages.ERROR,
                status=400
            )

        cart = CartService.get_cart_instance(request) # Instancia Classe Cart a partir da sessão

        # Tenta remover o item do carrinho usando o método remove_item da classe Cart, 
        # que retorna True se o item foi removido com sucesso.
        try:
            if cart.remove_item(variation_id):
                # Salva o carrinho atualizado na sessão do user
                CartService.save(request, cart)

                # Busca as variações restantes para recalcular os totais
                remaining_ids = cart.items.keys()
                # Evita consulta desnecessária ao banco de dados se o carrinho estiver vazio após a remoção
                variations = models.Variation.objects.filter(id__in=remaining_ids) if remaining_ids else []
                
                # Recalcula os totais atualizados para retornar na resposta AJAX
                totals = CartService.get_full_calculations(cart, variations)

                return self.render_message(
                    request,
                    message='Produto removido do carrinho',
                    level=django_messages.SUCCESS,
                    extra_data=totals,
                    status=200
                )

            return self.render_message(
                request,
                message='Produto não encontrado no carrinho',
                level=django_messages.ERROR,
                status=404
            )
        
        except Exception as e:
            # return JsonResponse({'status': 'error', 'message': 'Message: ' + str(e)}, status=500)
            return self.render_message(
                request,
                message='Ocorreu um erro ao remover o produto: ' + str(e),
                level=django_messages.ERROR,
                status=500
            )    

class UpdateItemSelectionCartView(View, MessageMixin):
    def post(self, request):
        # 'scope' define se a ação é em um item ('single'), em todos ('all') ou promocionais ('discounted')
        scope = request.POST.get('scope', 'single')
        is_selected = request.POST.get('selected') == 'true' # Convertendo string para booleano
        variation_id = request.POST.get('variation_id')      # 'variation_id' só é relevante quando o scope é 'single'
        
        cart = CartService.get_cart_instance(request)
        CartService.update_selection_by_scope(cart, scope, is_selected, variation_id)
        CartService.save(request, cart)

        variations = models.Variation.objects.filter(id__in=cart.items.keys())
        totals = CartService.get_full_calculations(cart, variations)

        return self.render_message(
            request,
            level=django_messages.SUCCESS,
            extra_data=totals,
            status=200
        )

class UpdateItemQuantityCartView(View, MessageMixin):
    def post(self, request):
        variation_id = request.POST.get('variation_id')
        try:
            new_qty = int(request.POST.get('new_qty', 1))
        except ValueError:
            return self.render_message(
                request,
                message='Quantidade inválida',
                level=django_messages.ERROR,
                status=400
            )

        # Validação de Estoque
        variation = get_object_or_404(models.Variation, id=variation_id)
        if new_qty > variation.stock:
            return self.render_message(
                request,
                message=f'Estoque insuficiente ({variation.stock} disponíveis)',
                level=django_messages.ERROR,
                status=400
            )

        # Atualização da Sessão
        cart = CartService.get_cart_instance(request)
        if variation_id in cart.items:
            # Sobrescreve a quantidade do item existente com a nova quantidade
            cart.add_or_update_item(new_qty, variation, overwrite=True)

        CartService.save(request, cart)
        variations = models.Variation.objects.filter(id__in=cart.items.keys())
        totals = CartService.get_full_calculations(cart, variations)

        return self.render_message(
            request,
            level=django_messages.SUCCESS,
            extra_data=totals,
            status=200
        )
