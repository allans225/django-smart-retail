from django.urls import path
from . import views

app_name = 'account'

urlpatterns = [
    # Página de Login e Registro
    path('auth/', views.AuthView.as_view(), name='auth_page'),

    # Endpoints para AJAX
    path('api/login/', views.LoginView.as_view(), name='login'),

    # Logout
    path('logout/', views.LogoutView.as_view(), name='logout'),
]