from django.db import models
from django.urls import reverse


from utils import generate
from utils.images import process_image_for_webp
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
            self.slug = generate.unique_slug(self)
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
    """
    Se possuir apenas uma variação é considerado "Simples". 
    Se tiver múltiplas variações, é "Variável".
    """
    type = models.CharField(
        default='S',
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

    @property
    def get_main_variation(self):
        """Retorna a variação principal (geralmente a mais barata)"""
        return self.variations.order_by('price').first()
    
    @property
    def total_stock(self):
        return sum(v.stock for v in self.variations.all())

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product:detail', args=[self.slug])
    
    def save(self, *args, **kwargs):
        if not self.slug:
            # Gera um slug único antes de salvar
            self.slug = generate.unique_slug(self)

        super().save(*args, **kwargs)

class Variation(models.Model):
    class Meta:
        verbose_name = "Variação"
        verbose_name_plural = "Variações"

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variations', verbose_name="Produto")
    name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nome da Variação")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Preço")
    promotional_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Preço Promocional")
    stock = models.PositiveIntegerField(default=1, verbose_name="Estoque")
    sku = models.CharField(
        max_length=50, 
        unique=True,
        blank=True,
        null=True,
        verbose_name="SKU (Código único)",
        help_text="Deixe em branco para gerar automaticamente"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name or f"Variação de {self.product.name}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if not self.sku:
            base = generate.sku(self.product.name, self.name)
            self.sku = f"{base}-{self.id}"
            
            # salvando novamente apenas o campo SKU para evitar loops
            # update() para mais eficiência, evitando a chamada recursiva do save()
            Variation.objects.filter(id=self.id).update(sku=self.sku)

class VariationImage(models.Model):
    class Meta:
        ordering = ['order']
        verbose_name = "Imagem da Variação"
        verbose_name_plural = "Imagens das Variações"

    variation = models.ForeignKey(
        Variation, on_delete=models.CASCADE, 
        related_name='images', verbose_name="Variação"
    )
    image = models.ImageField(
        upload_to=get_file_path, 
        max_length=255, verbose_name="Imagem"
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Ordem de Exibição")

    def __str__(self):
        return f"Imagem da {self.variation.name or self.variation.product.name}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
