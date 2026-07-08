from django.test import TestCase
from decimal import Decimal

from cart.entity.cart import Cart
from product.models import Category, Product, Variation

class CartEntityTestCase(TestCase):
    @classmethod
    def setUp(cls):
        cls.products = cls.instantiate_products()
        cls.cart = Cart()  # Inicializa o carrinho vazio para cada teste

    def test_add_or_update_item(self):
        cart = self.cart
        p1 = self.products[0]
        p2 = self.products[1]

        cart.add_or_update_item(1, p1) # Add 1 unidade do item (produto 1)
        cart.add_or_update_item(1, p1) # Add mais uma unidade do mesmo item (produto 1)
        cart.add_or_update_item(2, p2) # Add 2 unidades do item (produto 2)
        cart.add_or_update_item(1, p2, overwrite=True)  # Sobrescreve a quantidade para 1 (produto 2)

        self.assertEqual(cart.items[str(p1.id)]['qty'], 2) # Verifica se a quantidade do produto 1 é 2
        self.assertEqual(cart.items[str(p2.id)]['qty'], 1) # Verifica se a quantidade do produto 2 é 1 (sobrescrita)

    def test_remove_item(self):
        products = self.products
        cart = self.cart
        for p in products:
            cart.add_or_update_item(1, p)
        
        self.assertTrue(cart.remove_item(products[0].id))
        self.assertFalse(cart.remove_item(999))  # Tenta remover um item que não existe

    def test_remove_selected_items(self):
        products = self.products
        cart = self.cart
        for p in products:
            cart.add_or_update_item(1, p)

        cart.toggle_selection(products[1].id, is_selected=False) # Desmarca o segundo item para compra, então apenas o primeiro item está selecionado
        cart.remove_selected_items() # Removerá apenas o primeiro item, que está selecionado para compra

        self.assertNotIn(str(products[0].id), cart.items)  # O primeiro item deve ter sido removido
        self.assertIn(str(products[1].id), cart.items)     # O segundo item deve permanecer no carrinho

        selected_items = cart.get_selected_items_list(cart.items) # Obtém a lista de itens selecionados para compra
        self.assertEqual(len(selected_items), 0) # Todos os itens selecionados foram desmarcados para compra, então a lista deve estar vazia
        self.assertEqual(len(cart.items), 1) # Apenas o segundo item deve permanecer no carrinho 

    def test_toggle_selection(self):
        products = self.products
        cart = self.cart
        for p in products:
            cart.add_or_update_item(1, p)

        # Desmarca o primeiro item
        cart.toggle_selection(products[0].id, is_selected=False)
        self.assertFalse(cart.items[str(products[0].id)]['selected']) # Verifica se o item foi desmarcado
        self.assertTrue(cart.items[str(products[1].id)]['selected'])  # Verifica se o segundo item continua marcado
        selected_items = cart.get_selected_items_list(cart.items) # Obtém a lista de itens selecionados para compra
        self.assertEqual(len(selected_items), 1) # Apenas o segundo item deve estar selecionado para compra

    def test_add_item_exceeding_stock(self):
        p1 = self.products[0]

        self.cart.add_or_update_item(5, p1)  # Tenta adicionar 5 unidades, mas o estoque é apenas 2
        self.assertEqual(self.cart.items[str(p1.id)]['qty'], 2)  # A quantidade no carrinho deve ser limitada ao estoque disponível

    def test_update_item_to_zero_quantity_removes_it(self):
        p1 = self.products[0]
        self.cart.add_or_update_item(1, p1)  # Adiciona 1 unidade do item
        self.cart.add_or_update_item(0, p1, overwrite=True)  # Atualiza a quantidade para 0, o que deve remover o item do carrinho
        self.assertNotIn(str(p1.id), self.cart.items)  # Verifica se o item foi removido do carrinho

    @classmethod
    def instantiate_products(cls):
        """ Cria produtos e variações de teste para o carrinho """
        products = []
        category = Category.objects.create(
            name="Eletrônicos",
            description="Categoria de produtos eletrônicos"
        )

        product = Product.objects.create(
            name="Smartphone XYZ",
            short_description="Um smartphone incrível com recursos avançados.",
            long_description="Este smartphone possui uma tela de alta resolução, câmera de última geração e alto desempenho",
            type='S',
        )
        product.categories.set([category])  # Associa a categoria ao produto

        v1 = Variation.objects.create(
            id=1,
            product=product,
            name="Smartphone XYZ - 128GB",
            price=Decimal('999.99'),
            promotional_price=Decimal('899.99'),
            stock=2
        )

        v2 = Variation.objects.create(
            id=2,
            product=product,
            name="Smartphone XYZ - 256GB",
            price=Decimal('1099.99'),
            promotional_price=Decimal('0.00'),
            stock=2
        )
        products.append(v1)
        products.append(v2)
        return  products