from django.shortcuts import render, redirect
from django.views import View

from django.contrib import messages

class CheckoutSummaryView(View):
    template_name = 'order/order-summary.html'

    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            messages.warning(self.request, "Faça login para finalizar seu pedido.")
            return redirect('account:auth_page')
        
        return render(self.request, self.template_name, self.get_context())