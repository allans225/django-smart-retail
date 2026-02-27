document.addEventListener('DOMContentLoaded', function() {
    const cartList = document.querySelector('.cart-items-list');
    if (cartList) {
        cartList.addEventListener('change', async (e) => {
            // Verifica se o que mudou foi o checkbox de seleção do item
            if (e.target.classList.contains('cart-item-check')) {
                const variationId = e.target.dataset.id;
                const isSelected = e.target.checked;
                
                // Atualiza a seleção do item no servidor
                await updateItemSelection(variationId, isSelected);
            }
        });

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

async function updateItemSelection(variationId, isSelected) {
    const url = '/produtos/carrinho/update-selection/'; // URL para a view de atualização
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const formData = new FormData();
    formData.append('variation_id', variationId);
    formData.append('selected', isSelected);
    formData.append('csrfmiddlewaretoken', csrftoken);

    try {
        const response = await fetch(url, {
            method: 'POST',
            body: formData,
            headers: {'X-Requested-With': 'XMLHttpRequest'}
        });
        const data = await response.json();

        if (data.status === 'success') {
            updateSummary(data); // Atualiza os totais no DOM
        }
    } catch (error) {
        console.error('Erro:', error);
        showAlert('Erro de comunicação com o servidor', 'alert-danger');
    }
}

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
    // Seleciona os elementos do resumo para atualizar os valores
    const qtyEl = document.getElementById('total-qty');
    const subtotalEl = document.getElementById('subtotal-val');
    const discountPercentEl = document.getElementById('discount-percent-val');
    const discountAbsEl = document.getElementById('discount-abs-val');
    const grandTotalEl = document.getElementById('grand-total-val');

    changeSummaryDataVisibility(totals);

    // Usando exatamente os nomes das chaves enviadas pela UpdateItemSelectionView -> helper.get_cart_totals()
    if (qtyEl) 
        qtyEl.innerText = `x${totals.total_items_count}`;

    if (subtotalEl) 
        subtotalEl.innerText = formatMoney(totals.subtotal || totals.cart_subtotal);
    
    if (discountPercentEl) 
        discountPercentEl.innerText = `%${totals.total_discount_percent}`;
    
    if (discountAbsEl) 
        discountAbsEl.innerText = formatMoney(totals.total_discount);

    if (grandTotalEl) 
        grandTotalEl.innerText = formatMoney(totals.grand_total);
    
    // Atualiza a badge do header também
    if (typeof updateCartBadge === 'function') {
        updateCartBadge(totals.total_items_count);
    }
}

function changeSummaryDataVisibility(totals) {
    // Elementos de linha para possíveis alterações de estilo
    const rowSubtotal = document.getElementById('row-subtotal');
    const rowPercent = document.getElementById('row-discount-percent');
    const rowAbs = document.getElementById('row-discount-abs');

    // Controla a visibilidade das linhas de desconto com base nos valores recebidos
    if (rowPercent) {
        if (totals.total_discount_percent > 0) {
            document.getElementById('discount-percent-val').innerText = `%${totals.total_discount_percent}`;
            rowPercent.style.display = 'flex';
        } else {
            rowPercent.style.display = 'none';
            rowSubtotal.style.display = 'none';
        }
    }

    if (rowAbs) {
        if (totals.total_discount > 0) {
            document.getElementById('discount-abs-val').innerText = formatMoney(totals.total_discount);
            rowAbs.style.display = 'flex';
        } else {
            rowAbs.style.display = 'none';
            rowSubtotal.style.display = 'none';
        }
    }
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