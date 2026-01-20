from django.db import models
from datetime import date
from django.forms import ValidationError
from django.contrib.auth.models import User
from utils.validator.cpf import validate_cpf
from utils.validator.cep import validate_cep

class Profile(models.Model):
    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfis"

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Usuário")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Data de Nascimento")
    bio = models.TextField(null=True, blank=True, verbose_name="Biografia")
    cpf = models.CharField(max_length=11, unique=True, null=True, blank=True, verbose_name="CPF")

    # Propriedade para calcular a idade com base na data de nascimento
    @property
    def age(self):
        if self.birth_date:
            today = date.today()
            return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return None
    
    def clean(self):
        error_messages = {}

        if self.birth_date and self.birth_date > date.today():
            error_messages['birth_date'] = "A data de nascimento não pode ser no futuro."

        if self.cpf and not validate_cpf(self.cpf):
            error_messages['cpf'] = "CPF inválido."

        if error_messages:
            raise ValidationError(error_messages)

    def __str__(self):
        return f"Perfil de {self.user.get_full_name() or self.user.username}"

class Address(models.Model):
    class Meta:
        verbose_name = "Endereço"
        verbose_name_plural = "Endereços"

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='addresses', verbose_name="Perfil")
    street = models.CharField(max_length=128, verbose_name="Rua")
    number = models.CharField(max_length=10, verbose_name="Número")
    neighborhood = models.CharField(max_length=64, verbose_name="Bairro")
    supplement = models.CharField(max_length=128, blank=True, null=True, verbose_name="Complemento")
    city = models.CharField(max_length=64, verbose_name="Cidade")
    state = models.CharField(
        max_length=2, default="SP",
        choices=[
            ("AC", "Acre"),
            ("AL", "Alagoas"),
            ("AP", "Amapá"),
            ("AM", "Amazonas"),
            ("BA", "Bahia"),
            ("CE", "Ceará"),
            ("DF", "Distrito Federal"),
            ("ES", "Espírito Santo"),
            ("GO", "Goiás"),
            ("MA", "Maranhão"),
            ("MT", "Mato Grosso"),
            ("MS", "Mato Grosso do Sul"),
            ("MG", "Minas Gerais"),
            ("PA", "Pará"),
            ("PB", "Paraíba"),
            ("PR", "Paraná"),
            ("PE", "Pernambuco"),
            ("PI", "Piauí"),
            ("RJ", "Rio de Janeiro"),
            ("RN", "Rio Grande do Norte"),
            ("RS", "Rio Grande do Sul"),
            ("RO", "Rondônia"),
            ("RR", "Roraima"),
            ("SC", "Santa Catarina"),
            ("SP", "São Paulo"),
            ("SE", "Sergipe"),
            ("TO", "Tocantins"),
        ],
        verbose_name="Estado"   
    )
    zip_code = models.CharField(max_length=8, verbose_name="CEP")
    country = models.CharField(
        max_length=2, default="BR", 
        choices=[("BR", "Brasil")], 
        verbose_name="País")
    
    def clean(self):
        error_messages = {}

        if self.zip_code and not validate_cep(self.zip_code):
            error_messages['zip_code'] = "CEP inválido."

        if error_messages:
            raise ValidationError(error_messages)

    def __str__(self):
        return f"{self.street}, {self.number} - {self.profile.user.username}"
