from django.urls import path
from . import views

app_name = 'account'

urlpatterns = [
    # Página de Login e Registro
    path('auth/', views.AuthView.as_view(), name='auth_page'),
]