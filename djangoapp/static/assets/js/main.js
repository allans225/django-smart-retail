window.showAlert = (message, tags) => {
    let wrapper = document.querySelector('.messages-wrapper');

    if(!wrapper) {
        wrapper = document.createElement('section');
        wrapper.className = 'messages-wrapper';
        document.body.appendChild(wrapper);
    }

    const alertDiv = document.createElement('div');
    alertDiv.className = `alert ${tags}`;
    alertDiv.setAttribute('role', 'alert');

    let iconName = 'msg-debu.svg';
    if (tags === 'alert-success') iconName = 'msg-suss.svg';
    else if (tags === 'alert-danger') iconName = 'msg-dang.svg';
    else if (tags === 'alert-info') iconName = 'msg-info.svg';

    alertDiv.innerHTML = `
        <span class="alert-icon">
            <img src="/static/assets/img/icons/${iconName}" alt="Icon">
        </span>
        <span class="alert-text">${message}</span>
        <button class="alert-close" onclick="this.parentElement.remove();">
            <img src="/static/assets/img/icons/close-msg-small.svg" alt="Close">
        </button>
    `;
    wrapper.appendChild(alertDiv);

    setTimeout(() => {
        if (alertDiv.parentElement) alertDiv.remove();
    }, 5000);
}

// Função global para atualizar o contador do carrinho
window.updateCartBadge = (count) => {
    const badge = document.getElementById('cart-badge');
    if (!badge) return;

    const total = parseInt(count) || 0; // Garantir que count seja um número inteiro

    if (total > 0) {
        badge.innerText = total;
        badge.style.display = 'inline-block';
        badge.classList.add('badge-pulse');
        setTimeout(() => badge.classList.remove('badge-pulse'), 300);
    } else {
        badge.innerText = '';
        badge.style.display = 'none';
    }
};

// Função global para mudar a quantidade do produto (chamada pelo onclick dos botões + e -)
window.changeQty = (steps) =>{
    const qtyInput = document.getElementById('product-qty');
    if (!qtyInput) return;

    let currentVal = parseInt(qtyInput.value) || 1;
    const maxStock = parseInt(qtyInput.getAttribute('max')) || 1;

    let newVal = currentVal + steps;

    if (newVal >= 1 && newVal <= maxStock) {
        qtyInput.value = newVal;
    } else if (newVal > maxStock) {
        // Usa o seu showAlert que já está no escopo global/acessível
        showAlert(`Apenas ${maxStock} unidades disponíveis em estoque.`, 'alert-info');
    }
};