from django.shortcuts import render
from django.views.generic.list import ListView
from django.views import View

class ProductListView(ListView):
    pass

class CategoryList(View):
    pass

class DetailProduct(View):
    pass
