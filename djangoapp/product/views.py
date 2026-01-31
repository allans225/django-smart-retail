from django.shortcuts import render
from django.views.generic.list import ListView
from django.views import View
from . import models

class ProductListView(ListView):
    model = models.Product
    template_name = 'product/list-all.html'
    context_object_name = 'products'

class CategoryList(View):
    pass

class DetailProduct(View):
    pass
