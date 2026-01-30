from django.urls import path
from . import views

app_name = 'product'

urlpatterns = [
    # Listagem de TODOS os produtos
    path('all/', views.ProductListView.as_view(), name='all'),

    # URL Dinâmica para Categorias
    # dep = departamento
    path('dep/<slug:category_slug>/', views.CategoryList.as_view(), name='category_list'),

    # Detalhe do Produto dentro da Categoria
    path('dep/<slug:category_slug>/<slug:product_slug>/', views.DetailProduct.as_view(), name='detail'),
]