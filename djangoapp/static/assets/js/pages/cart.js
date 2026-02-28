import { CartAPI } from '../modules/api/cart.js';

const CartActions = {
    async toggleSelection(variationId, isSelected) {
        const url = '/produtos/carrinho/update-selection/';

        try {
            const data = await CartAPI.updateItemSelection(variationId, isSelected, url);
            if (data.status === 'success') {
                updateSummary(data);
            }
        } catch (error) {
            showAlert(error.message, error.tags)
        }
    },

    async removeItem(variationId, button) {
        const url = '/produtos/carrinho/remove/';
        try {
            const data = await CartAPI.remove(variationId, url);
            
            if (data.status === 'success') {
                const card = button.closest('.cart-item-card');
                // Animação de saída
                card.style.opacity = '0';
                card.style.transform = 'translateX(20px)';
                card.style.transition = 'all 0.3s ease';

                setTimeout(() => {
                    card.remove();
                    if (data.total_items_count === 0) {
                        location.reload(); // Recarrega a página para mostrar o estado do carrinho vazio
                        return;
                    } 
                    updateSummary(data);
                }, 300);
                showAlert(data.message, 'alert-success');
            }
        } catch (error) {
            showAlert(error.message, error.tags);
        }
    }
};

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    const cartList = document.querySelector('.cart-items-list');
    
    if (cartList) {
        // Delegação para Checkbox
        cartList.addEventListener('change', (e) => {
            if (e.target.classList.contains('cart-item-check')) {
                CartActions.toggleSelection(e.target.dataset.id, e.target.checked);
            }
        });

        // Delegação para Botão Remover
        cartList.addEventListener('click', (e) => {
            const removeBtn = e.target.closest('.remove-btn');
            if (removeBtn) {
                CartActions.removeItem(removeBtn.dataset.id, removeBtn);
            }
        });
    }
});

/**
 * Funções de UI (Resumo e Formatação)
 */
function updateSummary(totals) {
    const qtyEl = document.getElementById('total-qty');
    const subtotalEl = document.getElementById('subtotal-val');
    const grandTotalEl = document.getElementById('grand-total-val');

    if (qtyEl) qtyEl.innerText = `x${totals.total_items_count}`;
    if (subtotalEl) subtotalEl.innerText = formatMoney(totals.cart_subtotal);
    if (grandTotalEl) grandTotalEl.innerText = formatMoney(totals.grand_total);

    // Visibilidade dos descontos
    changeSummaryDataVisibility(totals);

    if (typeof updateCartBadge === 'function') {
        updateCartBadge(totals.total_items_count);
    }
}

function changeSummaryDataVisibility(totals) {
    const rowSubtotal = document.getElementById('row-subtotal');
    const rowPercent = document.getElementById('row-discount-percent');
    const rowAbs = document.getElementById('row-discount-abs');

    const hasDiscount = totals.total_discount_percent > 0;

    if (rowPercent) {
        rowPercent.style.display = hasDiscount ? 'flex' : 'none';
        if (hasDiscount) document.getElementById('discount-percent-val').innerText = `%${totals.total_discount_percent}`;
    }

    if (rowAbs) {
        rowAbs.style.display = hasDiscount ? 'flex' : 'none';
        if (hasDiscount) document.getElementById('discount-abs-val').innerText = formatMoney(totals.total_discount);
    }

    // O rowSubtotal (preço riscado) só deve aparecer se houver desconto
    if (rowSubtotal) {
        rowSubtotal.style.display = hasDiscount ? 'flex' : 'none';
    }
}

function formatMoney(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}