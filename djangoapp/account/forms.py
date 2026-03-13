from django import forms

class BasicAuthData(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'auth-input', 'placeholder': 'Email'}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'auth-input', 'placeholder': 'Senha'}))

class LoginForm(BasicAuthData):
    remember = forms.BooleanField(required=False)