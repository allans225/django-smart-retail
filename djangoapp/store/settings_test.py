from .settings import *

# Acelerar os testes usando o MD5PasswordHasher, que é mais rápido que os hashers padrão.
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Não disparar e-mails reais durante os testes, usar o backend de e-mail em memória.
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'