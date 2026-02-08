from django.contrib import admin
from .models import Product, Variation, Category
from utils.filters import price_filter

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

class VariationInline(admin.StackedInline):
    model = Variation
    extra = 1
    min_num = 1 # Garante que pelo menos uma variação (estoque/preço) seja criada
    # Melhor organização dos campos da variação para leitura e edição mais fácil
    fields = [
        ('name', 'sku'), 
        ('price', 'promotional_price', 'stock')
    ]

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'display_price', 'display_total_un', 'updated_at']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['categories']
    search_fields = ['name', 'slug']
    list_filter = ['type', 'categories']
    inlines = [VariationInline]

    # Organização do formulário do Produto em seções
    fieldsets = (
        ('Informações de Marketing', {
            'fields': ('name', 'slug', 'type', 'categories')
        }),
        ('Conteúdo', {
            'fields': ('short_description', 'long_description'),
        }),
        ('Mídia', {
            'fields': ('cover_image',),
        }),
    )

    def display_price(self, obj):
        main_var = obj.get_main_variation
        if main_var:
            return price_filter(main_var.price)
        return "N/A"
    
    display_price.short_description = 'Preço'

    def display_total_un(self, obj):
        return obj.total_stock
    
    display_total_un.short_description = 'Total Un.'

admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)