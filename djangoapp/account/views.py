from django.contrib import messages
from django.conf import settings

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from django.db import transaction

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from .models import Profile
from .models import Address

from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views import View
from .forms import \
    LoginForm,  RegisterForm, UserBasicDataUpdateForm, \
    UserSecurityDataUpdateForm, UserAddressDataUpdateForm

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.shortcuts import redirect
from utils.validator.address import get_user_default_address, get_user_addresses

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
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
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
                }, status=500)
            
        # Se o form não for válido, retorna os erros específicos dos campos
        return JsonResponse({
            'status': 'error',
            'message': 'Verifique os dados informados.',
            'errors': form.errors.get_json_data()
        }, status=400)

class SetupPanelView(LoginRequiredMixin, TemplateView):
    template_name = 'account/setup-panel.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        initial_basic_data = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'birth_date': user.profile.birth_date if hasattr(user, 'profile') else '',
            'cpf': user.profile.cpf if hasattr(user, 'profile') else '',
            'biography': user.profile.bio if hasattr(user, 'profile') else '',
        }

        default = get_user_default_address(user)
        addresses = get_user_addresses(user)

        initial_address_data = {
            'zip_code': default.zip_code if default else '',
            'number': default.number if default else '',
            'street': default.street if default else '',
            'neighborhood': default.neighborhood if default else '',
            'city': default.city if default else '',
            'state': default.state if default else '',
            'country': default.country if default else '',
            'complement': default.complement if default else '',
        }

        initial_security_data = {
            'email': user.email,
            'username': user.username,
        }

        context['basic_data_form'] = UserBasicDataUpdateForm(
            initial=initial_basic_data, 
            profile=user.profile
        )
        context['security_data_form'] = UserSecurityDataUpdateForm(initial=initial_security_data)
        context['address_data_form'] = UserAddressDataUpdateForm(initial=initial_address_data)

        context['states'] = Address._meta.get_field('state').choices
        context['countries'] = Address._meta.get_field('country').choices

        context['saved_addresses'] = addresses if addresses else []
        print("Saved addresses:", context['saved_addresses'])  # Debugging line to check saved addresses
        return context
    
class UpdateBasicDataView(LoginRequiredMixin, View):
    def post(self, request):
        user = request.user
        profile, _ = Profile.objects.get_or_create(user=user)  # Garante que o profile exista
        form = UserBasicDataUpdateForm(request.POST, profile=profile)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user.first_name = form.cleaned_data.get('first_name')
                    user.last_name = form.cleaned_data.get('last_name')
                    user.save()

                    profile.birth_date = form.cleaned_data.get('birth_date')
                    profile.cpf = form.cleaned_data.get('cpf')
                    profile.bio = form.cleaned_data.get('biography')
                    profile.save()

                return JsonResponse({
                    'status': 'success',
                    'message': 'Perfil atualizado com sucesso!'
                })
                
            except Exception as e:
                # erro do banco de dados ou interno
                return JsonResponse({
                    'status': 'error',
                    'message': f'Erro ao salvar os dados: {str(e)}'
                }, status=500)
        else:
            # formulário inválido, retorna os erros para o JS exibir
            return JsonResponse({
                'status': 'error',
                'message': 'Verifique os dados informados',
                'errors': form.errors.get_json_data() # envia os erros de validação
            }, status=400)

class UpdateSecurityDataView(LoginRequiredMixin, View):
    def post(self, request):
        form = UserSecurityDataUpdateForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = request.user
                    email = form.cleaned_data.get('email')
                    username = form.cleaned_data.get('username')
                    new_password = form.cleaned_data.get('new_password')
                    has_changes = False

                    if email and email != user.email:
                        user.email = email
                        has_changes = True

                    if username and username != user.username:
                        user.username = username
                        has_changes = True

                    # Atualiza a senha apenas se o campo não estiver vazio e se passar na validação do form
                    if new_password:
                        user.set_password(new_password)
                        has_changes = True

                    if has_changes:
                        user.save()
                        if new_password:
                            update_session_auth_hash(request, user)  # Mantém o usuário logado após a mudança de senha

                return JsonResponse({
                    'status': 'success',
                    'message': 'Dados atualizados com sucesso!'
                })
                
            except Exception as e:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Erro ao salvar os dados: {str(e)}'
                }, status=500)
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Verifique os dados informados',
                'errors': form.errors.get_json_data()
            }, status=400)

class UpdateAddressDataView(LoginRequiredMixin, View):
    def post(self, request):
        form = UserAddressDataUpdateForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = request.user
                    
                    # Desempacotando a tupla corretamente (ignora o booleano)
                    profile, created = Profile.objects.get_or_create(user=user)
                    
                    # Busca o primeiro endereço do perfil. Se não existir, cria uma nova instância.
                    address = Address.objects.filter(profile=profile).first()
                    if not address:
                        address = Address(profile=profile, is_default=True)

                    # Atualizando os campos
                    address.zip_code = form.cleaned_data.get('zip_code')
                    address.number = form.cleaned_data.get('number')
                    address.street = form.cleaned_data.get('street')
                    address.neighborhood = form.cleaned_data.get('neighborhood')
                    address.city = form.cleaned_data.get('city')
                    address.state = form.cleaned_data.get('state')
                    address.country = form.cleaned_data.get('country')
                    address.complement = form.cleaned_data.get('complement')
                
                    address.full_clean()
                    address.save()

                return JsonResponse({
                    'status': 'success',
                    'message': 'Endereço atualizado com sucesso!'
                })

            except Exception as e:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Erro ao salvar os dados: {str(e)}'
                }, status=500)
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Verifique os dados informados',
                'errors': form.errors.get_json_data()
            }, status=400)
