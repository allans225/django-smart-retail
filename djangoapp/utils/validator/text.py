import re
from django.core.exceptions import ValidationError

def validate_no_special_chars(value):
    """
    Verifica se a string contém apenas letras e espaços.
    Aceita caracteres acentuados latinos.
    """
    # r'^[a-zA-ZÀ-ÿ\s]+$'
    if not re.match(r'^[a-zA-ZÀ-ÿ\s]+$', value):
        raise ValidationError(
            'Este campo não deve conter números ou caracteres especiais.'
        )
