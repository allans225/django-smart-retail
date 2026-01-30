from django.db import models

from utils.images import process_image_for_webp
from utils.slug import generate_unique_slug
from utils.files import get_file_path

class Category(models.Model):
    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=100, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self)
        super().save(*args, **kwargs)

class Product(models.Model):
    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"

    name = models.CharField(max_length=100)
    short_description = models.TextField(max_length=255, verbose_name="Descrição Curta")
    long_description = models.TextField(verbose_name="Descrição Longa")
    cover_image = models.ImageField(
        upload_to=get_file_path,
        max_length=255,
        blank=True, null=True, 
        verbose_name="Imagem de Capa")
    slug = models.SlugField(
        max_length=255,
        unique=True, blank=True
    )
    marketing_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço Marketing")
    promotional_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Preço Promocional")
    type = models.CharField(
        default='V',
        max_length=1,
        choices=[
            ('V', 'Variável'),
            ('S', 'Simples'),
        ],
        verbose_name="Tipo"
    )
    categories = models.ManyToManyField(
        Category, 
        related_name='products',
        verbose_name="Categorias"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            # Gera um slug único antes de salvar
            self.slug = generate_unique_slug(self)

        super().save(*args, **kwargs)

        if self.cover_image:
            # Processa a imagem para WebP e redimensiona
            new_path = process_image_for_webp(self.cover_image)

            if new_path:
                # Atualiza o campo da imagem com o novo caminho WebP
                self.__class__.objects.filter(id=self.id).update(cover_image=new_path)
                self.cover_image.name = new_path

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
