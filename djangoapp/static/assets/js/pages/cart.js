import { CartAPI } from '../modules/api/cart.js';

const CartActions = {
    // marcou ou desmarcou um item do carrinho
    async toggleSelection(variationId, isSelected) {
        const url = '/produtos/carrinho/update-selection/';

        // Usuário marcou/desmarcou um item, então ele personalizou o carrinho. Logo desmarcamos os filtros globais, se ativos.
        unmarkGlobalCartFilters();

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
    },

    async handleFilterSelection(scope, isSelected) {
        const url = '/produtos/carrinho/update-selection/';
        toggleGlobalCartFilters(scope, isSelected);
        try {
            const data = await CartAPI.updateBatchSelection(scope, isSelected, url);
            
            if (data.status === 'success') {
                // atualiza visualmente todos os checkboxes da lista
                this.syncCheckboxesUI(scope, isSelected);
                updateSummary(data);
            }
        } catch (error) {
            showAlert(error.message, 'alert-danger');
        }
    },

    syncCheckboxesUI(scope, isSelected) {
        const checks = document.querySelectorAll('.cart-item-check');
        checks.forEach(check => {
            if (scope === 'all') {
                check.checked = isSelected;
            } else if (scope === 'discounted') {
                // captura e verifica o data-attribute no HTML do item (data-has-discount="true")
                if (check.dataset.hasDiscount === 'true') {
                    check.checked = isSelected;
                } else {
                    // se filtrar por "com desconto", os sem desconto devem desmarcar
                    if(isSelected) check.checked = false;
                }
            }
        });
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

    // Seleção dos Filtros do carrinho por ID
    const filterAll = document.getElementById('filter-all');
    const filterDiscount = document.getElementById('filter-discount');

    [filterAll, filterDiscount].forEach(filter => {
        if (filter) {
            filter.addEventListener('change', (e) => {
                const scope = e.target.id === 'filter-all' ? 'all' : 'discounted';
                CartActions.handleFilterSelection(scope, e.target.checked);
            });
        }
    });
});

/**
 * Funções de UI
 */
function updateSummary(totals) {
    const qtyEl = document.getElementById('total-qty');
    const subtotalEl = document.getElementById('subtotal-val');
    const grandTotalEl = document.getElementById('grand-total-val');

    if (qtyEl) qtyEl.innerText = `x${totals.selected_items_count}`;
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
    const rowTotalQty = document.getElementById('row-total-qty');

    const hasSelectedItems = totals.selected_items_count > 0;
    const hasDiscount = totals.total_discount_percent > 0;

    if (hasSelectedItems)
        rowTotalQty.style.display = hasSelectedItems ? 'flex' : 'none';

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

function unmarkGlobalCartFilters() {
    const filterAll = document.getElementById('filter-all');
    const filterDiscount = document.getElementById('filter-discount');
    if (filterAll) filterAll.checked = false;
    if (filterDiscount) filterDiscount.checked = false;
}

function toggleGlobalCartFilters(scope, isSelected) {
    const filterAll = document.getElementById('filter-all');
    const filterDiscount = document.getElementById('filter-discount');

    if (scope === 'all' && isSelected) {
        if (filterDiscount) filterDiscount.checked = false;
    } else if (scope === 'discounted' && isSelected) {
        if (filterAll) filterAll.checked = false;
    }
}

function formatMoney(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}