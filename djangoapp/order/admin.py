from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    
    # Campos que o admin pode apenas visualizar, nunca alterar
    readonly_fields = (
        'display_image', 'product_name', 'product_id', 
        'variation_name', 'variation_id', 'price', 
        'promotional_price', 'quantity', 'created_at'
    )
    
    # Organiza quais campos aparecem na tabela
    fields = (
        'display_image', 'product_name', 'price', 
        'quantity', 'variation_name'
    )

    def display_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image}" style="width: 50px; height: auto;">')
        return "Sem imagem"
    display_image.short_description = 'Imagem'

class OrderAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'total', 'status', 'created_at')
    list_display_links = ('pk', 'user')
    # 'list_editable' permite mudar o status sem entrar no pedido
    list_editable = ('status',) 
    
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'pk')
    
    inlines = [OrderItemInline]
    
    # Ordenar pelos mais recentes por padrão
    ordering = ('-created_at',)

admin.site.register(Order, OrderAdmin)
