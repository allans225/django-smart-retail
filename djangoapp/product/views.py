from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views import View
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.contrib.messages import constants as django_messages
from django.conf import settings
from utils.helper import cart_calculations as cart_helper
from . import models

class ProductListView(ListView):
    model = models.Product
    template_name = 'product/list.html'
    context_object_name = 'products'
    paginate_by = 20

    def get_queryset(self):
        queryset = models.Product.objects.all() # Fetch all products
        return queryset

class DetailProduct(DetailView):
    model = models.Product
    template_name = 'product/detail.html'
    context_object_name = 'product'
    slug_url_kwarg = 'slug'

    
class CartDetailView(View):
    def get(self, request, *args, **kwargs):
        cart_session = request.session.get('cart', {})
        
        variation_ids = cart_session.keys()
        variations = models.Variation.objects.filter(
            id__in=variation_ids
        ).select_related('product')

        cart_items = []
        for variation in variations:
            vid_str = str(variation.id)
            item_data = cart_session.get(vid_str, {})

            # Garante que pegamos os dados do dicionário da sessão
            quantity = item_data.get('qty', 0) if isinstance(item_data, dict) else item_data
            is_selected = item_data.get('selected', True) if isinstance(item_data, dict) else True

            price_eff = variation.get_price()
            
            cart_items.append({
                'variation': variation,
                'quantity': quantity,
                'selected': is_selected,  # Adiciona o estado de seleção ao contexto do item
                'item_subtotal_raw': variation.price * quantity,
                'item_grand_total': price_eff * quantity,
            })

        totals = cart_helper.get_cart_totals(cart_session, variations)

        context = {
            'cart_items': cart_items,
            **totals 
        }
        return render(request, 'product/cart.html', context)

class AddToCartView(View):
    def post(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') != 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'Acesso negado'}, status=400)

        # Garante que o ID seja tratado como String para a Sessão
        variation_id = request.POST.get('variation_id')
        if not variation_id:
            return JsonResponse({'status': 'error', 'message': 'ID da variação ausente'}, status=400)
            
        try:
            quantity = int(request.POST.get('quantity', 1))
        except (ValueError, TypeError):
            quantity = 1

        variation = get_object_or_404(models.Variation, id=variation_id)

        # Validação de estoque
        if variation.stock < quantity:
            return JsonResponse({
                'status': 'error',
                'message': f'Estoque insuficiente ({variation.stock} disponíveis).',
                'tags': settings.MESSAGE_TAGS.get(django_messages.ERROR, 'alert-danger')
            }, status=400)

        cart = request.session.get('cart', {})
        
        # forçando a chave a ser string para evitar erros de serialização JSON
        vid_str = str(variation_id)

        if vid_str in cart:
            # Se for dicionário, atualiza qty
            if isinstance(cart[vid_str], dict):
                cart[vid_str]['qty'] = min(cart[vid_str]['qty'] + quantity, variation.stock)
            else:
                # Se for int (formato antigo), converte para dict
                old_qty = cart[vid_str]
                cart[vid_str] = {'qty': min(old_qty + quantity, variation.stock), 'selected': True}
        else:
            cart[vid_str] = {'qty': quantity, 'selected': True}

        request.session['cart'] = cart
        request.session.modified = True

        # soma o total de itens
        total_items_count = cart_helper.get_cart_items_count(cart)

        return JsonResponse({
            'status': 'success',
            'message': f'Adicionado: {variation.product.name} ({variation.name})',
            'tags': settings.MESSAGE_TAGS.get(django_messages.SUCCESS, 'alert-success'),
            'total_items_count': total_items_count,
        })

class RemoveFromCartView(View):
    def post(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') != 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'Acesso negado'}, status=400)
        
        variation_id = request.POST.get('variation_id')
        
        # se não houver ID ou se o ID for a string 'null'
        if not variation_id or variation_id == 'null':
            return JsonResponse({'status': 'error', 
                                 'message': 'ID da variação inválido'
                                 }, status=400)

        cart_session = request.session.get('cart', {})
        var_id_str = str(variation_id)

        if var_id_str in cart_session:
            # Remove o item
            del cart_session[var_id_str]
            request.session['cart'] = cart_session
            request.session.modified = True

            # Busca as variações que SOBRARAM para recalcular os totais
            remaining_ids = cart_session.keys()
            variations = models.Variation.objects.filter(id__in=remaining_ids)
            
            # Helper centralizado realiza os cálculos...
            totals = cart_helper.get_cart_totals(cart_session, variations)

            return JsonResponse({
                'status': 'success',
                'message': 'Produto removido do carrinho',
                **totals
            })
        
        return JsonResponse({'status': 'error', 
                             'message': 'Item não encontrado no carrinho'
                             }, status=404)
    
class UpdateItemSelectionView(View):
    def post(self, request, *args, **kwargs):
        variation_id = request.POST.get('variation_id')
        is_selected = request.POST.get('selected') == 'true' # Convertendo string para booleano

        cart = request.session.get('cart', {})
        vid_str = str(variation_id)

        if vid_str in cart:
            if isinstance(cart[vid_str], dict):
                cart[vid_str]['selected'] = is_selected
            else:
                # Converte para dict se ainda for int
                cart[vid_str] = {'qty': cart[vid_str], 'selected': is_selected}
            
            request.session.modified = True

        # recálculo dos totais
        # Buscamos as variações presentes no carrinho para o helper calcular
        variations = models.Variation.objects.filter(id__in=cart.keys())
        totals = cart_helper.get_cart_totals(cart, variations)

        return JsonResponse({
            'status': 'success',
            'cart_subtotal': totals['cart_subtotal'],
            'total_discount': totals['total_discount'],
            'total_discount_percent': totals['total_discount_percent'],
            'grand_total': totals['grand_total'],
            'total_items_count': totals['total_items_count'],
        })