from django.contrib import messages
from django.conf import settings

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.shortcuts import redirect

from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views import View
from .forms import LoginForm

class AuthView(TemplateView):
    template_name = 'account/login-register.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('account:auth_page')

class LoginView(View):
    def post(self, request):
        form = LoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data.get('email')
            passw = form.cleaned_data.get('password')
            remember = form.cleaned_data.get('remember')

            try:
                # buscando usuário pelo email
                # o '__iexact' ignora se é maiúsculo ou minúsculo:
                user_obj = User.objects.get(email__iexact=email)
                # autenticando usando o username (Django exige) e senha
                user = authenticate(request, username=user_obj.username, password=passw)

                if user is not None:
                    login(request, user)
                    messages.success(request, f'Bem-vindo de volta, {user.first_name or user.username}!')

                    # lógica para "Lembrar-me"
                    if not remember:
                        request.session.set_expiry(0) # expira ao fechar o navegador
                    else:
                        # usa o padrão definido no settings. Se a constante sumir do settings.py, usa o valor padrão (1209600)
                        age = getattr(settings, 'SESSION_COOKIE_AGE_REMEMBER', 1209600)
                        request.session.set_expiry(age)
                    return JsonResponse({
                        'status': 'success',
                        'redirect': '/produtos/all/'
                    })
                else:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Credenciais inválidas.'
                    }, status=401)

            except User.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Credenciais inválidas.'
                }, status=401)
        
        # Bad request - se o form não for válido (ex: e-mail mal digitado)
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
