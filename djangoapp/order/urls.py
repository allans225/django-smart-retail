from django.urls import path
from . import views

app_name = 'order'

urlpatterns = [
    path('checkout/summary/', views.CheckoutSummaryView.as_view(), name='checkout_summary'),
    path('create/', views.CreateOrderView.as_view(), name='create_order'),
]