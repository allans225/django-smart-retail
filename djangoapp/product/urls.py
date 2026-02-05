from django.urls import path
from . import views

app_name = 'product'

urlpatterns = [
    path('all/', views.ProductListView.as_view(), name='all'),

    path('categoria/<slug:category_slug>/', views.ProductListView.as_view(), name='category_list'),

    path('<slug:slug>/', views.DetailProduct.as_view(), name='detail'),
]