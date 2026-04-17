from django.contrib import messages
from django.conf import settings

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from django.db import transaction

from django.contrib.auth.models import User
from .models import Profile
from .models import Address

from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views import View
from .forms import LoginForm, RegisterForm

from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.contrib.auth import logout

class AuthView(TemplateView):
    template_name = 'account/auth.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['form'] = RegisterForm()
        context['states'] = Address._meta.get_field('state').choices
        context['countries'] = Address._meta.get_field('country').choices

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
            
            except Exception as e:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Erro inesperado: {str(e)}'
                }, status=400)
        
        # Bad request - se o form não for válido (ex: e-mail mal digitado)
        return JsonResponse({'status': 'error', 'errors': form.errors.get_json_data()}, status=400)
    
class RegisterView(View):
    def post(self, request):
        form = RegisterForm(request.POST)

        if form.is_valid():
            try:
                # transação segura no DB: caso falhe a criação do Profile o User não deve existir (rollback)
                with transaction.atomic():
                    # Criando o User
                    user = User.objects.create_user(
                        username=form.cleaned_data['username'],
                        email=form.cleaned_data['email'],
                        password=form.cleaned_data['password'],
                        first_name=form.cleaned_data['first_name'],
                        last_name=form.cleaned_data['last_name'],
                    )

                    # Criando o Profile
                    profile = Profile(user=user, birth_date=form.cleaned_data.get('birth_date'))
                    profile.full_clean() # Validações no método do model
                    profile.save()
                    
                    zipcode = form.cleaned_data.get('zip_code')
                    if zipcode:
                        Address.objects.create(
                            profile=profile,
                            zip_code=zipcode,
                            number=form.cleaned_data.get('number'),
                            street=form.cleaned_data.get('street'),
                            neighborhood=form.cleaned_data.get('neighborhood'),
                            city=form.cleaned_data.get('city'),
                            state=form.cleaned_data.get('state'),
                            country=form.cleaned_data.get('country'),
                            complement=form.cleaned_data.get('complement'),
                        )

                # Logar o usuário automaticamente
                login(request, user)
                messages.success(request, f"Bem-vindo, {user.first_name}! Cadastro realizado com sucesso.")

                return JsonResponse({
                    'status': 'success',
                    'redirect': '/produtos/all/'
                })
            
            except DjangoValidationError as e:
                # Captura erros do full_clean() do Model
                return JsonResponse({
                    'status': 'error',
                    'message': 'Erro de validação. Verifique os dados!',
                    'errors': e.message_dict  # Envia os erros para o JS printar nos campos
                }, status=400)

            except IntegrityError:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Erro de validação. Verifique os dados!'
                }, status=400)
            
            except Exception as e:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Erro inesperado: {str(e)}'
                }, status=400)
            
        # Se o form não for válido, retorna os erros específicos dos campos
        return JsonResponse({
            'status': 'error',
            'message': 'Verifique os dados informados.',
            'errors': form.errors.get_json_data()
        }, status=400)