document.addEventListener('DOMContentLoaded', function() {
    const cartList = document.querySelector('.cart-items-list');
    if (cartList) {
        cartList.addEventListener('click', async(e) => {
            // Permite clicar tanto no botão quanto na imagem dentro do botão
            const removeBtn = e.target.closest('.remove-btn') || e.target.closest('.remove-btn img');
            if (removeBtn) {
                const variationId = removeBtn.dataset.id;
                await removeFromCart(variationId, removeBtn);
            }
        });
    }
});

async function removeFromCart(variationId, button) {
    const url = '/produtos/carrinho/remove/'; // URL para a view de remoção
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    const formData = new FormData();
    formData.append('variation_id', variationId);
    formData.append('csrfmiddlewaretoken', csrfToken);

    try {
        const response = await fetch(url, {
            method: 'POST',
            body: formData,
            headers: {'X-Requested-With': 'XMLHttpRequest'}
        });
        const data = await response.json();

        if (data.status === 'success') {
            // Efeito visual de remoção
            const card = button.closest('.cart-item-card');
            card.style.opacity = '0';
            card.style.transform = 'translateX(20px)';
            card.style.transition = 'all 0.3s ease';

            updateCartBadge(data.total_items_count);
            showAlert(data.message, 'alert-success');

            setTimeout(() => {
                card.remove();
                // Se o carrinho ficar vazio, exibe a mensagem de carrinho vazio
                if (data.total_items_count === 0) {
                    location.reload(); // Recarrega a página para mostrar o estado de carrinho vazio
                    return;
                }
                // Atualiza os totais no DOM
                updateSummary(data);

                // todo: Atualiza o contador de itens no header
            }, 300);
        } else {
            showAlert(data.message || 'Erro ao remover item', 'alert-danger');
        }
    } catch (error) {
        console.error('Erro:', error);
        showAlert('Erro de comunicação com o servidor', 'alert-danger');
    }
}

function updateSummary(totals) {
    // Atualiza os elementos do resumo com os novos valores
    const qtyEl = document.getElementById('total-qty');
    const subtotalEl = document.getElementById('subtotal-val');
    const discountPercentEl = document.getElementById('discount-percent-val');
    const discountAbsEl = document.getElementById('discount-abs-val');
    const grandTotalEl = document.getElementById('grand-total-val');

    if (qtyEl) qtyEl.innerText = `x${totals.total_items_count}`;
    if (subtotalEl) subtotalEl.innerText = formatMoney(totals.cart_subtotal);
    if (discountPercentEl) discountPercentEl.innerText = `%${totals.total_discount_percent}`;
    if (discountAbsEl) discountAbsEl.innerText = formatMoney(totals.total_discount);
    if (grandTotalEl) grandTotalEl.innerText = formatMoney(totals.grand_total);
}

/* 
    Função utilitária para formatar valores monetários no formato brasileiro
    Formatação no lado cliente, price_filter (templatetags do Django) no lado servidor. 
    Ambos utilizam Intl para consistência
*/
function formatMoney(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
};