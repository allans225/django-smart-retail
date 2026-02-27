from django.urls import path
from . import views

app_name = 'product'

urlpatterns = [
    path('all/', views.ProductListView.as_view(), name='all'),
    path('categoria/<slug:category_slug>/', views.ProductListView.as_view(), name='category_list'),
    path('carrinho/', views.CartDetailView.as_view(), name='cart_detail'),
    path('carrinho/add/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('carrinho/remove/', views.RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('carrinho/update-selection/', views.UpdateItemSelectionView.as_view(), name='update_cart_selection'),
    path('<slug:slug>/', views.DetailProduct.as_view(), name='detail'),
]