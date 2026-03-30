from django import forms
from datetime import datetime
from django.contrib.auth.models import User
from .models import Address
from django.core.validators import MinLengthValidator, MaxLengthValidator, EmailValidator

from django.contrib.auth.password_validation import validate_password
from utils.validator.text import validate_no_special_chars
from utils.validator.cep import look_up_cep

class BasicAuthData(forms.Form):
    email = forms.EmailField(
        validators=[EmailValidator(message="Informe um e-mail válido.")],
        widget=forms.EmailInput(attrs={'class': 'auth-input', 'placeholder': 'Email'})
    )
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'auth-input', 'placeholder': 'Senha'}))

class LoginForm(BasicAuthData):
    remember = forms.BooleanField(required=False)

class RegisterForm(BasicAuthData):
    first_name = forms.CharField(
        validators=[
            validate_no_special_chars,
            MinLengthValidator(2, message="O nome deve ter pelo menos 2 caracteres"),
            MaxLengthValidator(30, message="O nome deve ter menos de 30 caracteres")
        ],
        widget=forms.TextInput(attrs={'class': 'auth-input', 'placeholder': 'Nome'})
    )
    last_name = forms.CharField(
        validators=[
            validate_no_special_chars,
            MinLengthValidator(2, message="O sobrenome deve ter pelo menos 2 caracteres"),
            MaxLengthValidator(30, message="O sobrenome deve ter menos de 30 caracteres")
        ],
        widget=forms.TextInput(attrs={'class': 'auth-input', 'placeholder': 'Sobrenome'})
    )
    username = forms.CharField(
        validators=[
            MinLengthValidator(2, message="O nome de usuário deve ter pelo menos 2 caracteres"),
            MaxLengthValidator(30, message="O nome de usuário deve ter menos de 20 caracteres")
        ],
        widget=forms.TextInput(attrs={'class': 'auth-input', 'placeholder': 'Nome de Usuário'})
    )
    birth_date = forms.CharField(widget=forms.TextInput(attrs={'class': 'auth-input', 'placeholder': 'Data de Aniversário'}))
    confirm_passw = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'auth-input', 'placeholder': 'Confirmar Senha'}))

    # campos de endereço são OPCIONAIS no formulário de registro de usuário.
    zip_code = forms.CharField(max_length=8, required=False,widget=forms.TextInput(attrs={'placeholder': 'CEP'}))
    number = forms.CharField(max_length=10, required=False, widget=forms.TextInput(attrs={'placeholder': 'Número'}))
    street = forms.CharField(max_length=128, required=False, widget=forms.TextInput(attrs={'placeholder': 'Rua'}))
    neighborhood = forms.CharField(max_length=64, required=False, widget=forms.TextInput(attrs={'placeholder': 'Bairro'}))
    city = forms.CharField(max_length=64, required=False, widget=forms.TextInput(attrs={'placeholder': 'Cidade'}))
    state = forms.ChoiceField(required=False, choices=Address._meta.get_field('state').choices)
    country = forms.ChoiceField(required=False, choices=Address._meta.get_field('country').choices)
    supplement = forms.CharField(max_length=128, required=False, widget=forms.TextInput(attrs={'placeholder': 'Complemento'}))

    # Garante que a ordem dos dados no Python bata com o HTML
    field_order = [
        'first_name', 'last_name', 'birth_date', 'username', 'email', 'password', 'confirm_passw', # user data
        'zip_code', 'number', 'street', 'neighborhood', 'city', 'state', 'country', 'supplement' # user address
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

    def clean_birth_date(self):
        date = self.cleaned_data.get('birth_date')

        if not date:
            raise forms.ValidationError("A data de nascimento é obrigatória.")
        try:
            # Converte o formato yyyy-mm-dd para um objeto date
            return datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise forms.ValidationError("Formato de data inválido")
        
    def clean_zip_code(self):
        cep = self.cleaned_data.get('zip_code')
        # campo não obrigatório
        if not cep:
            return cep
        # se preenchido, validamos na API
        if not look_up_cep(cep):
            raise forms.ValidationError("CEP inválido ou não encontrado.")
        return cep
