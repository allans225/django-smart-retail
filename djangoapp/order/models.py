from django.db import models
from django.contrib.auth.models import User

class Order(models.Model):
    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuário")
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Preço Total do Pedido")
    total_items = models.PositiveIntegerField(default=0, verbose_name="Total de Itens")
    status = models.CharField(
        default="C", max_length=1,
        choices=[
            ("A", "Aprovado"),
            ("C", "Criado"),
            ("P", "Pendente"),
            ("R", "Reprovado"),
            ("E", "Enviado"),
            ("F", "Finalizado"),
        ],
        verbose_name="Status do Pedido"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    def __str__(self):
        return f"Pedido N. {self.pk}"

class OrderItem(models.Model):
    class Meta:
        verbose_name = "Item do Pedido"
        verbose_name_plural = "Itens do Pedido"

    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name="Pedido")
    product_name = models.CharField(max_length=100, verbose_name="Nome do Produto")
    product_id = models.PositiveIntegerField(verbose_name="ID do Produto")
    variation_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Variação")
    variation_id = models.PositiveIntegerField(verbose_name="ID da Variação")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Preço")
    promotional_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Preço Promocional")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Quantidade")
    image = models.CharField(max_length=2000, blank=True, null=True, verbose_name="Imagem")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    def __str__(self):
        return f"Item {self.name_product} do Pedido N. {self.order.pk}"
    
