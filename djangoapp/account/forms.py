from django import forms
from datetime import datetime
from django.contrib.auth.models import User
from .models import Address, Profile
from django.core.validators import MinLengthValidator, MaxLengthValidator, EmailValidator

from django.contrib.auth.password_validation import validate_password
from utils.validator.text import validate_no_special_chars
from utils.validator.cep import look_up_cep
from utils.validator import cpf as cpf_utils

class BaseUserDataForm(forms.Form):
    first_name = forms.CharField(
        validators=[
            validate_no_special_chars,
            MinLengthValidator(1, message="O nome deve ter pelo menos 1 caracteres"),
            MaxLengthValidator(30, message="O nome deve ter menos de 30 caracteres")
        ],
        widget=forms.TextInput(attrs={'class': 'auth-input', 'placeholder': 'Nome'})
    )
    last_name = forms.CharField(
        validators=[
            validate_no_special_chars,
            MinLengthValidator(1, message="O sobrenome deve ter pelo menos 1 caracteres"),
            MaxLengthValidator(30, message="O sobrenome deve ter menos de 30 caracteres")
        ],
        widget=forms.TextInput(attrs={'class': 'auth-input', 'placeholder': 'Sobrenome'})
    )
    birth_date = forms.CharField(widget=forms.TextInput(attrs={'class': 'auth-input', 'placeholder': 'Data de Aniversário'}))

    def clean_birth_date(self):
        date = self.cleaned_data.get('birth_date')

        if not date:
            raise forms.ValidationError("A data de nascimento é obrigatória.")
        try:
            # Converte o formato yyyy-mm-dd para um objeto date
            return datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise forms.ValidationError("Formato de data inválido")

class BasicAuthData(forms.Form):
    email = forms.EmailField(
        validators=[EmailValidator(message="Informe um e-mail válido.")],
        widget=forms.EmailInput(attrs={'class': 'auth-input', 'placeholder': 'Email'})
    )
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'auth-input', 'placeholder': 'Senha'}))

class LoginForm(BasicAuthData):
    remember = forms.BooleanField(required=False)

class RegisterForm(BasicAuthData, BaseUserDataForm):
    username = forms.CharField(
        validators=[
            MinLengthValidator(2, message="O nome de usuário deve ter pelo menos 2 caracteres"),
            MaxLengthValidator(30, message="O nome de usuário deve ter menos de 20 caracteres")
        ],
        widget=forms.TextInput(attrs={'class': 'auth-input', 'placeholder': 'Nome de Usuário'})
    )
    confirm_passw = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'auth-input', 'placeholder': 'Confirmar Senha'}))

    # campos de endereço são OPCIONAIS no formulário de registro de usuário.
    zip_code = forms.CharField(max_length=8, required=False,widget=forms.TextInput(attrs={'placeholder': 'CEP'}))
    number = forms.CharField(max_length=10, required=False, widget=forms.TextInput(attrs={'placeholder': 'Número'}))
    street = forms.CharField(max_length=128, required=False, widget=forms.TextInput(attrs={'placeholder': 'Rua'}))
    neighborhood = forms.CharField(max_length=64, required=False, widget=forms.TextInput(attrs={'placeholder': 'Bairro'}))
    city = forms.CharField(max_length=64, required=False, widget=forms.TextInput(attrs={'placeholder': 'Cidade'}))
    state = forms.ChoiceField(required=False, choices=Address._meta.get_field('state').choices)
    country = forms.ChoiceField(required=False, choices=Address._meta.get_field('country').choices)
    complement = forms.CharField(max_length=128, required=False, widget=forms.TextInput(attrs={'placeholder': 'Complemento'}))

    # Garante que a ordem dos dados no Python bata com o HTML
    field_order = [
        'first_name', 'last_name', 'birth_date', 'username', 'email', 'password', 'confirm_passw', # user data
        'zip_code', 'number', 'street', 'neighborhood', 'city', 'state', 'country', 'complement' # user address
    ]

    # Métodos de validação
    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        confirm_passw = cleaned_data.get("confirm_passw")

        if password and confirm_passw and password != confirm_passw:
            raise forms.ValidationError("As senhas não coincidem.")

        return cleaned_data
    
    def clean_email(self):
        email = self.cleaned_data.get('email')  
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este e-mail já está cadastrado.")
        return email
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            try:
                validate_password(password)
            except forms.ValidationError as e:
                raise forms.ValidationError(e.messages)
        return password

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Nome de usuário já cadastrado.")
        return username
        
    def clean_zip_code(self):
        cep = self.cleaned_data.get('zip_code')
        # campo não obrigatório
        if not cep:
            return cep
        # se preenchido, validamos na API
        if not look_up_cep(cep):
            raise forms.ValidationError("CEP inválido ou não encontrado.")
        return cep

class UserBasicDataUpdateForm(BaseUserDataForm):
    cpf = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'CPF'}),
        max_length=14,
    )

    biography = forms.CharField(
        required=False,
        max_length=564,
        widget=forms.Textarea(attrs={
            'placeholder': 'Diga-nos sobre a sua história.',
            'rows': 4,
            'maxlength': '564' 
        })
    )

    def __init__(self, *args, **kwargs):
        self.profile = kwargs.pop('profile', None)
        super().__init__(*args, **kwargs)

        # Se o perfil do usuário já tiver um CPF, definimos o campo como somente leitura
        if self.profile and self.profile.cpf: 
            self.fields['cpf'].widget.attrs['readonly'] = 'readonly' # apenas para exibição, não permite edição
            self.fields['cpf'].help_text = "O CPF não pode ser alterado uma vez definido."
            current_class = self.fields['cpf'].widget.attrs.get('class', '')
            self.fields['cpf'].widget.attrs['class'] = f"{current_class} input-readonly".strip() # Adiciona uma classe CSS para estilizar o campo como somente leitura
            self.fields['cpf'].initial = self.profile.cpf  # Define o valor inicial do campo como o CPF existente

    def clean_cpf(self):
        if self.profile and self.profile.cpf:
            return self.profile.cpf

        cpf = self.cleaned_data.get('cpf')

        # Campo opcional
        if not cpf:
            return None

        cleaned_cpf = cpf_utils.clean_data(cpf)

        # Valida usando o CPF limpo
        if not cpf_utils.validate_cpf(cleaned_cpf):
            raise forms.ValidationError("CPF inválido.")

        # Consulta duplicidade no banco usando o CPF limpo
        query = Profile.objects.filter(cpf=cleaned_cpf)
        
        # Se o perfil atual estiver definido, excluímos ele da consulta para evitar conflito consigo mesmo
        if self.profile and self.profile.pk:
            query = query.exclude(pk=self.profile.pk)

        if query.exists():
            raise forms.ValidationError("Este CPF já está em uso por outro usuário.")

        return cleaned_cpf

class UserSecurityDataUpdateForm(forms.Form):
    # Campos de segurança do usuário com required=False para permitir atualizações parciais
    email = forms.EmailField(
        required=False,
        validators=[EmailValidator(message="Informe um e-mail válido.")],
        widget=forms.EmailInput(attrs={'class': 'auth-input', 'placeholder': 'Email'})
    )
    username = forms.CharField(
        required=False,
        validators=[
            MinLengthValidator(2, message="O nome de usuário deve ter pelo menos 2 caracteres"),
            MaxLengthValidator(30, message="O nome de usuário deve ter menos de 20 caracteres")
        ],
        widget=forms.TextInput(attrs={'class': 'auth-input', 'placeholder': 'Nome de Usuário'})
    )
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'auth-input', 'placeholder': 'Senha'})
    )
    new_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'auth-input', 'placeholder': 'Nova Senha'})
    )
    confirm_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'auth-input', 'placeholder': 'Confirmar Nova Senha'})
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Recebe o usuário atual
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Só valida se o email foi preenchido e se for diferente do atual
        if email and self.user and self.user.email != email:
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError("Este e-mail já está em uso por outra conta.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Só valida se o username foi preenchido e se for diferente do atual
        if username and self.user and self.user.username != username:
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError("Este nome de usuário já está em uso.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        # Se o usuário deseja alterar a senha, ele deve fornecer a senha atual
        if new_password or confirm_password:
            if not password:
                self.add_error('password', "A senha atual é obrigatória para alterar a senha.")
            elif not self.user.check_password(password):
                self.add_error('password', "A senha atual está incorreta.")

            if new_password != confirm_password:
                self.add_error('confirm_password', "As novas senhas não coincidem.")
            else:
                # Validar a nova senha usando os validadores do Django
                try:
                    validate_password(new_password, user=self.user)
                except forms.ValidationError as e:
                    self.add_error('new_password', e.messages)

        return cleaned_data

class UserAddressDataUpdateForm(forms.Form):
    # Campos obrigatórios para atualização de endereço do usuário
    zip_code = forms.CharField(max_length=8, required=True,widget=forms.TextInput(attrs={'placeholder': 'CEP'}))
    number = forms.CharField(max_length=10, required=True, widget=forms.TextInput(attrs={'placeholder': 'Número'}))
    street = forms.CharField(max_length=128, required=True, widget=forms.TextInput(attrs={'placeholder': 'Rua'}))
    neighborhood = forms.CharField(max_length=64, required=True, widget=forms.TextInput(attrs={'placeholder': 'Bairro'}))
    city = forms.CharField(max_length=64, required=True, widget=forms.TextInput(attrs={'placeholder': 'Cidade'}))
    state = forms.ChoiceField(required=True, choices=Address._meta.get_field('state').choices)
    country = forms.ChoiceField(required=True, choices=Address._meta.get_field('country').choices)
    complement = forms.CharField(max_length=128, required=True, widget=forms.TextInput(attrs={'placeholder': 'Complemento'}))

    def clean_zip_code(self):
        cep = self.cleaned_data.get('zip_code')
        if not look_up_cep(cep):
            raise forms.ValidationError("CEP inválido ou não encontrado.")
        return cep
