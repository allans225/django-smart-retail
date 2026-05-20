from django.contrib import messages as django_messages
from django.http import JsonResponse

class MessageMixin:
    """ 
    Mixin para padronizar notificações em Views.
    Suporte: requisições AJAX (JSON) e tradicionais (Django messages framework).
    """
    def render_message(self, request, message=None, level=django_messages.SUCCESS, extra_data=None, status=200):
        # Obtém a tag amigável para o nível de mensagem (success, error, warning, info)
        tag = django_messages.DEFAULT_TAGS.get(level, 'info')

        # Lógica para req AJAX
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            data = {
                'status': 'success' if status < 400 else 'error',
                'message': message,
                'tags': tag,
            }
            if extra_data:
                data.update(extra_data) # Permite adicionar dados extras como totais atualizados, contagem de itens, etc.
            return JsonResponse(data, status=status)
        
        # Lógica para req tradicional
        django_messages.add_message(request, level, message)
        return None  # A View deve lidar com o redirecionamento
