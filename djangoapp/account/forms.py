from django import forms
from django.contrib.auth.models import User

class BasicAuthData(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'auth-input', 'placeholder': 'Email'}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'auth-input', 'placeholder': 'Senha'}))

class LoginForm(BasicAuthData):
    remember = forms.BooleanField(required=False)

class RegisterForm(BasicAuthData):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'auth-input', 'placeholder': 'Nome'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'auth-input', 'placeholder': 'Sobrenome'}))
    birth_date = forms.CharField(widget=forms.TextInput(attrs={'class': 'auth-input', 'placeholder': 'Data de Aniversário'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'auth-input', 'placeholder': 'Nome de Usuário'}))
    confirm_passw = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'auth-input', 'placeholder': 'Confirmar Senha'}))

    # Garante que a ordem dos dados no Python bata com o HTML
    field_order = ['first_name', 'last_name', 'birth_date', 'username', 'email', 'password', 'confirm_passw']

    # Métodos de validação
    def clean(self):
        cleaned_data = super().clean

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
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Nome de usuário já cadastrado.")
        return username