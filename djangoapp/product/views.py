from django.views.generic.list import ListView
from . import models

class ProductListView(ListView):
    model = models.Product
    template_name = 'product/list.html'
    context_object_name = 'products'

    def get_queryset(self):
        queryset = models.Product.objects.all() # Fetch all products
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class DetailProduct(ListView):
    ...
