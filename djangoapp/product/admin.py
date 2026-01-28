from django.contrib import admin
from .models import Product, Variation, Category

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

class VariationInline(admin.TabularInline):
    model = Variation
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'marketing_price', 'promotional_price', 'type', 'created_at', 'updated_at')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [
        VariationInline
    ]

admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)