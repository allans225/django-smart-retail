from account.models import Address

def get_user_address(user):
    """Busca o endereço vinculado ao Perfil do usuário logado."""
    try:
        return Address.objects.select_related('profile') \
            .filter(profile__user=user) \
            .first()
    except Address.DoesNotExist:
        return None
