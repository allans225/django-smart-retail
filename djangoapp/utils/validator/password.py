import re
from django.core.exceptions import ValidationError

class ComplexityValidator:
    def validate(self, password, user=None):
        errors = []
        if not re.search(r'[A-Z]', password):
            errors.append("uma letra maiúscula")
        if not re.search(r'[a-z]', password):
            errors.append("uma letra minúscula")
        if not re.search(r'[0-9]', password):
            errors.append("um número")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("um caractere especial")

        if errors:
            raise ValidationError(
                f"A senha deve conter: {', '.join(errors)}."
            )

    def get_help_text(self):
        return "Sua senha deve conter no mínimo 8 caracteres, incluíndo uma letras maiúscula, minúscula, número e símbolo."
