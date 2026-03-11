from django.views.generic import TemplateView

class AuthView(TemplateView):
    template_name = 'account/login-register.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context