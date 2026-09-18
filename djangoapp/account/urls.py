from django.urls import path
from . import views

app_name = 'account'

urlpatterns = [
    # Página de Login e Registro
    path('auth/', views.AuthView.as_view(), name='auth_page'),

    # Página de Configurações dos Dados do Usuário/Perfil dados básicos, endereço e segurança
    path('dashboard/', views.DashBoardHomeView.as_view(), name='dashboard'),
    path('dashboard/address/', views.DashBoardAddressView.as_view(), name='dashboard_address'),
    path('dashboard/security/', views.DashBoardSecurityView.as_view(), name='dashboard_security'),
    path('dashboard/profile/', views.DashBoardProfileView.as_view(), name='dashboard_profile'),

    path('dashboard/profile/remove-picture', views.delete_profile_picture_view, name='delete_profile_picture'),
    path('dashboard/profile/update-picture', views.update_profile_picture_view, name='dashboard_update_picture'),

    # auth API endpoints 
    path('api/login/', views.LoginView.as_view(), name='login'),
    path('api/register/', views.RegisterView.as_view(), name='register'),
    
    # Logout
    path('logout/', views.LogoutView.as_view(), name='logout'),
]