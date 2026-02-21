from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views import View
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.contrib.messages import constants as django_messages
from django.conf import settings
from . import models

class ProductListView(ListView):
    model = models.Product
    template_name = 'product/list.html'
    context_object_name = 'products'
    paginate_by = 20

    def get_queryset(self):
        queryset = models.Product.objects.all() # Fetch all products
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class DetailProduct(DetailView):
    model = models.Product
    template_name = 'product/detail.html'
    context_object_name = 'product'
    slug_url_kwarg = 'slug'

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
            cart[vid_str] = min(cart[vid_str] + quantity, variation.stock)
        else:
            cart[vid_str] = quantity

        request.session['cart'] = cart
        request.session.modified = True

        # soma o total de itens
        total_items = sum(cart.values()) if cart else 0

        return JsonResponse({
            'status': 'success',
            'message': f'Adicionado: {variation.product.name} ({variation.name})',
            'tags': settings.MESSAGE_TAGS.get(django_messages.SUCCESS, 'alert-success'),
            'cart_count': total_items
        })
    
class CartDetailView(View):
    def get(self, request, *args, **kwargs):
        cart_session = request.session.get('cart', {})
        cart_items = []
        
        cart_subtotal = 0  # Valor total SEM descontos
        grand_total = 0    # Valor total COM descontos
        total_items_count = sum(cart_session.values()) if cart_session else 0

        variation_ids = cart_session.keys()
        variations = models.Variation.objects.filter(id__in=variation_ids).select_related('product')

        for variation in variations:
            quantity = cart_session.get(str(variation.id), 0)
            
            # Preço subtotal (sem promoção)
            price_raw = variation.price
            item_subtotal_raw = price_raw * quantity
            cart_subtotal += item_subtotal_raw

            # Preço real cobrado (com ou sem promoção)
            price_effective = variation.promotional_price if variation.promotional_price > 0 else variation.price
            item_grand_total = price_effective * quantity
            grand_total += item_grand_total

            cart_items.append({
                'variation': variation,
                'quantity': quantity,
                'item_subtotal_raw': item_subtotal_raw,
                'item_grand_total': item_grand_total,
            })

        # Cálculo do desconto absoluto
        total_discount = cart_subtotal - grand_total

        # Cálculo do percentual (com "trava de segurança")
        total_discount_percent = round((total_discount / cart_subtotal) * 100, 2) if cart_subtotal > 0 else 0

        context = {
            'cart_items': cart_items,
            'total_items': total_items_count,
            'cart_subtotal': cart_subtotal, 
            'grand_total': grand_total,
            'total_discount': total_discount,
            'total_discount_percent': total_discount_percent,
        }

        return render(request, 'product/cart.html', context)
