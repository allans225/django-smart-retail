class Cart:
    def __init__(self, session_cart_data=None):
        """ Inicializa o carrinho a partir dos dados da sessão, garantindo que seja um dicionário válido. """
        self._items = session_cart_data if isinstance(session_cart_data, dict) else {}

    @property
    def items(self):
        return self._items

    def to_dict(self):
        """ Retorna uma cópia do dicionário de itens do carrinho. """
        return self._items
    
    def remove_item(self, item_id):
        """ Remove um item do carrinho com base no ID da variação. Retorna True se o item foi removido """
        id_str = str(item_id)
        if id_str in self._items:
            del self._items[id_str]
            return True
        return False

    def remove_selected_items(self):
        """ Remove todos os itens que estão selecionados para compra """
        for vid in self.get_selected_item_ids():
            self.remove_item(vid)

    def add_or_update_item(self, required_quantity, item, overwrite=False):
        """
        Adiciona ou atualiza (substitui) um item no carrinho, respeitando o estoque disponível.
        - overwrite=True:  Substitui a quantidade existente pela nova quantity (required_quantity).
        - overwrite=False: Soma quantity à quantidade existente.
        """
        id_str = str(item.id)
        current_qty = 0

        if id_str in self._items:
            data = self._items[id_str]
            current_qty = data['qty'] if isinstance(data, dict) else int(data)
        
        if overwrite:
            # Sobrescreve a quantidade, garantindo que seja entre 0 e o estoque
            new_quantity = min(max(0, required_quantity), item.stock)
        else:
            # Calcula a nova quantidade, garantindo que não ultrapasse o estoque
            new_quantity = min(current_qty + required_quantity, item.stock)

        # Se a quantidade for zero ou negativa, removemos o item do carrinho
        if new_quantity <= 0:
            if id_str in self._items:
                del self._items[id_str]
            return

        price = item.get_price() # Preço com desconto aplicado, se houver
        self._items[id_str] = {
            'qty': new_quantity,
            'price': float(price),
            'total_price': float(price * new_quantity),
            'selected': True,
            'product_name': item.product.name,
            'variation_name': item.name,
        }

    def toggle_selection(self, item_id=None, is_selected=None):
        """ Altera o estado de seleção de um item ou de todos os itens """
        if item_id:
            id_str = str(item_id)
            if id_str in self._items:
                self._update_item_selection(id_str, is_selected)
        else:
            for id_str in self._items.keys():
                self._update_item_selection(id_str, is_selected)
    
    def _update_item_selection(self, id_str, state):
        """ Método auxiliar para garantir a normalização durante o update de seleção """
        if not isinstance(self._items[id_str], dict):
            self._items[id_str] = {'qty': self._items[id_str], 'selected': state}
        else:
            self._items[id_str]['selected'] = state

    def get_selected_items_list(self, variations_dict):
        """ Recebe um dicionário de Variations e retorna uma lista de dicts para templates """
        items = []
        for vid in self.get_selected_item_ids():
            data = self.items.get(vid)
            item = variations_dict.get(str(vid))

            if item and data:
                items.append({
                    'variation': item,
                    'quantity': data['qty'],
                    'price': data['price'],
                    'total_price': data['qty'] * data['price'],
                })

        return items

    def get_selected_item_ids(self):
        """ Retorna ids de itens no carrinho que foram selecionados para a compra """
        return [id for id, data in self.items.items() if data.get('selected')]
