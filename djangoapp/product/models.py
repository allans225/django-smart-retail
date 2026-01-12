from django.db import models

from django.utils.text import slugify
from utils.resizing.images import resize_image

class Product(models.Model):
    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"

    name = models.CharField(max_length=100)
    short_description = models.TextField(max_length=255, verbose_name="Descrição Curta")
    long_description = models.TextField(verbose_name="Descrição Longa")
    cover_image = models.ImageField(
        upload_to='products/%Y/%m/%d/',
        blank=True, null=True, 
        verbose_name="Imagem de Capa")
    slug = models.SlugField(unique=True, blank=True, null=True)
    marketing_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço Marketing")
    promotional_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Preço Promocional")
    type = models.CharField(
        default='V',
        max_length=1,
        choices=[
            ('V', 'Variação'),
            ('S', 'Simples'),
        ],
        verbose_name="Tipo"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

        if self.cover_image:
            # max_image_size = 800
            resize_image(self.cover_image) # padrão de 800px

class Variation(models.Model):
    class Meta:
        verbose_name = "Variação"
        verbose_name_plural = "Variações"

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variations', verbose_name="Produto")
    name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nome da Variação")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Preço")
    promotional_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Preço Promocional")
    stock = models.PositiveIntegerField(default=1, verbose_name="Estoque")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name or f"Variação de {self.product.name}"
