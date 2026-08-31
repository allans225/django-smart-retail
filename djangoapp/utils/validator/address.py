from account.models import Address

def get_user_default_address(user):
    """Busca o endereço padrão vinculado ao Perfil do usuário logado."""
    try:
        return Address.objects.select_related('profile') \
            .filter(profile__user=user, is_default=True) \
            .first()
    except Address.DoesNotExist:
        return None

def get_user_addresses(user):
    """Busca todos os endereços vinculados ao Perfil do usuário logado."""
    try:
        return Address.objects.select_related('profile') \
            .filter(profile__user=user) \
            .all()
    except Address.DoesNotExist:
        return None
