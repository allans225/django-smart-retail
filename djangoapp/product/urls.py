from django.urls import path
from . import views

app_name = 'product'

urlpatterns = [
    # Produtos e Categorias
    path('all/', views.ProductListView.as_view(), name='all'),
    path('categoria/<slug:category_slug>/', views.ProductListView.as_view(), name='category_list'),

    # Carrinho - Visualização e Ações Básicas
    path('carrinho/', views.CartDetailView.as_view(), name='cart_detail'),
    path('carrinho/add/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('carrinho/remove/', views.RemoveFromCartView.as_view(), name='remove_from_cart'),
    
    # Carrinho - Atualizações Dinâmicas (AJAX)
    path('carrinho/update-selection/', views.UpdateItemSelectionCartView.as_view(), name='update_selection'),
    path('carrinho/update-quantity/', views.UpdateItemQuantityCartView.as_view(), name='update_quantity'),

    # Detalhe do Produto
    path('<slug:slug>/', views.DetailProduct.as_view(), name='detail'),
]