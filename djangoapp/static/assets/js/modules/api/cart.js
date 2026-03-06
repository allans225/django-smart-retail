// Script especialista para lidar com as interações do carrinho
// via API (adicionar, remover, atualizar quantidades)

export const CartAPI = {
    async add(variationId, quantity, url) {
        const formData = getFormDataCart(variationId);
        formData.append('quantity', quantity);
        return await getPostData(url, formData);
    },

    async updateItemSelection(variationId, isSelected, url) {
        const formData = getFormDataCart(variationId);
        formData.append('selected', isSelected);
        return await getPostData(url, formData);
    },

    async remove(variationId, url) {
        const formData = getFormDataCart(variationId);
        return await getPostData(url, formData);
    },

    async updateBatchSelection(scope, isSelected, url) {
        const formData = getFormDataCart(); // chamada com parâmetro no padrão nulo
        formData.append('scope', scope);    // 'all' ou 'discounted'
        formData.append('selected', isSelected ? 'true' : 'false');
        return await getPostData(url, formData);
    },

    async updateQuantity(variationId, newVal, url) {
        const formData = getFormDataCart(variationId);
        formData.append('new_qty', newVal); // alinhado com request.POST.get('new_qty'), class UpdateItemQuantityCartView()
        return await getPostData(url, formData);
    }
};

// Função para coletar o token CSRF e criar um FormData básico para o cart
function getFormDataCart(variationId=null) {
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const formData = new FormData();
    formData.append('csrfmiddlewaretoken', csrftoken);

    if (variationId == null) return formData;

    formData.append('variation_id', variationId);
    return formData;
}

// Função genérica para fazer requisições POST e lidar com erros
async function getPostData(url, formData) {
    const response = await fetch(url, {
        method: 'POST',
        body: formData,
        headers: {'X-Requested-With': 'XMLHttpRequest'}
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw {
            status: response.status,
            message: errorData.message || 'Falha na comunicação com o servidor',
            tags: errorData.tags || 'alert-danger'
        };
    }
    return await response.json();
}