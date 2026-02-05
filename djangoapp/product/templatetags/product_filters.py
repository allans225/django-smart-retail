from django.template import Library
from utils import filters

register = Library()

@register.filter
def price_filter(value):
    return filters.price_filter(value)