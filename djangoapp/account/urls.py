from django.urls import path
from . import views

app_name = 'account'

urlpatterns = [
    # Página de Login e Registro
    path('auth/', views.AuthView.as_view(), name='auth_page'),

    # Página de Configurações dos Dados do Usuário/Perfil
    path('setup-panel/', views.SetupPanelView.as_view(), name='user_setup'),

    # Endpoints para AJAX
    path('api/login/', views.LoginView.as_view(), name='login'),
    path('api/register/', views.RegisterView.as_view(), name='register'),
    path('api/update/basic-data', views.UpdateBasicDataView.as_view(), name='upt_basic_data'),
    path('api/update/security-data', views.UpdateSecurityDataView.as_view(), name='upt_security_data'),
    path('api/update/address-data', views.UpdateAddressDataView.as_view(), name='upt_address_data'),

    # Logout
    path('logout/', views.LogoutView.as_view(), name='logout'),
]