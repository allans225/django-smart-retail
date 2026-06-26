from django.urls import reverse
from django.db.utils import IntegrityError
from decimal import Decimal
from django.test import TestCase
from product.models import Category, Product, Variation

class ProductModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(
            name="Eletrônicos",
            description="Categoria de produtos eletrônicos"
        )

        cls.product = Product.objects.create(
            name="Smartphone XYZ",
            short_description="Um smartphone incrível com recursos avançados.",
            long_description="Este smartphone possui uma tela de alta resolução, câmera de última geração e alto desempenho",
            type='S',
        )

        cls.product.categories.set([cls.category])  # Associa a categoria ao produto

        cls.v1 = Variation.objects.create(
            product=cls.product,
            name="Smartphone XYZ - 128GB",
            price=Decimal('999.99'),
            promotional_price=Decimal('899.99'),
            stock=10
        )

        cls.v2 = Variation.objects.create(
            product=cls.product,
            name="Smartphone XYZ - 256GB",
            price=Decimal('1099.99'),
            promotional_price=Decimal('999.99'),
            stock=10
        )

    def test_product_creation(self):
        """ Testa a criação de um produto e verifica se os campos estão corretos. """
        self.assertEqual(self.product.name, "Smartphone XYZ")
        self.assertEqual(self.product.short_description, "Um smartphone incrível com recursos avançados.")
        self.assertEqual(self.product.long_description, "Este smartphone possui uma tela de alta resolução, câmera de última geração e alto desempenho")
        self.assertEqual(self.product.type, 'S')
        self.assertIsNotNone(self.product.slug)
        self.assertEqual(self.product.slug, "smartphone-xyz")
        self.assertIn(self.category, self.product.categories.all()) # Verifica se a categoria está associada ao produto

    def test_variation_creation(self):
        """ Testa a criação de variações e verifica se os campos estão corretos. """
        self.assertEqual(self.v1.name, "Smartphone XYZ - 128GB")
        self.assertEqual(self.v1.price, Decimal('999.99'))
        self.assertEqual(self.v1.promotional_price, Decimal('899.99'))
        self.assertEqual(self.v1.stock, 10)
        self.assertEqual(self.v1.product, self.product)  # Verifica se a variação está associada ao produto correto
        self.assertIsNotNone(self.v1.sku)

    # Product Model Methods Tests - Happy path:

    def test_product_str_method(self):
        """ Testa o método __str__ do produto, retornando o nome do produto. """
        self.assertEqual(str(self.product), "Smartphone XYZ")

    def test_get_main_variation(self):
        """ Testa o método get_main_variation, retornando a variação com o menor preço. """
        main_variation = self.product.get_main_variation
        self.assertEqual(main_variation, self.v1) # v1 tem o menor preço

    def test_total_stock(self):
        """ Testa o método total_stock, retornando a soma do estoque de todas as variações. """
        total_stock = self.product.total_stock
        self.assertEqual(total_stock, 20) # v1 + v2 = 10 + 10 = 20

    def test_get_absolute_url(self):
        """ Testa o método get_absolute_url, retornando a URL do detalhe do produto. """
        url = self.product.get_absolute_url()
        expected_url = reverse('product:detail', kwargs={'slug': self.product.slug}) # Pega a url de forma dinâmica usando o nome da view e o slug do produto
        self.assertEqual(url, expected_url)

    # Variation Model Methods Tests - Happy path:

    def test_variation_str_method(self):
        """ Testa o método __str__ da variação, retornando o nome da variação. """
        self.assertEqual(str(self.v1), "Smartphone XYZ - 128GB")
        self.assertEqual(str(self.v2), "Smartphone XYZ - 256GB")
    
    def test_variation_sku_uniqueness(self):
        """ Garante que o banco de dados impede a criação de variações com o mesmo SKU. """
        # Força a criação de uma variação com o mesmo SKU da v1
        with self.assertRaises(IntegrityError):
            Variation.objects.create(
                product=self.product,
                name="Smartphone XYZ - 128GB Duplicate",
                price=Decimal('999.99'),
                promotional_price=Decimal('899.99'),
                stock=10,
                sku=self.v1.sku  # Força o mesmo SKU da v1
            )

    def test_get_variation_price(self):
        """ 
        Testa o método get_variation_price, retornando o preço da variação. 
        Retorna o preço promocional se for menor que o preço normal 
        """
        self.assertEqual(self.v1.get_price(), Decimal('899.99')) 
        self.assertEqual(self.v2.get_price(), Decimal('999.99'))