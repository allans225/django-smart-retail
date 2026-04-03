const messageTimeOut = (msg, value = 5000) => {
    setTimeout(() => {
        msg.style.opacity = '0';
        setTimeout(() => {
            if (msg.parentElement) msg.remove();
        }, 500); // tempo para o fade-out terminar
    }, value);
}

/* 
 * Renderiza a mensagem que fica guardada na sessão do servidor 
 * e aparece automaticamente assim que a nova página carregar.
 * Resolve o problema: redirecionamento limpa o estado do JavaScript e carrega uma nova página, 
 * qualquer alerta disparado via AJAX antes do redirecionamento sumiria instantaneamente.
 */
const processDjangoMessages = () => {
    const messagesElement = document.getElementById('django-messages');
    
    if (messagesElement) {
        try {
            const messages = JSON.parse(messagesElement.textContent);
            
            messages.forEach(msg => {
                if (window.showAlert) {
                    window.showAlert(msg.message, msg.tags);
                }
            });
            
            // Remove o elemento após processar para evitar duplicidade
            messagesElement.remove();
        } catch (e) {
            console.error("Erro ao processar mensagens do Django:", e);
        }
    }
};
// Inicia o processamento quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', processDjangoMessages);

window.showAlert = (message, tags) => {
    // Se 'tag' for undefined ou null, assume 'error' como padrão
    const providedTag = tags || 'error';
    let wrapper = document.querySelector('.messages-wrapper');

    if(!wrapper) {
        wrapper = document.createElement('section');
        wrapper.className = 'messages-wrapper';
        document.body.appendChild(wrapper);
    }

    let finalClass = '';
    
    // Lógica de detecção e mapeamento de tags vindas do Django
    if (providedTag.startsWith('alert-')) {
        finalClass = providedTag;
    } else {
        const tagMap = {
            'error': 'alert-danger',
            'success': 'alert-success',
            'warning': 'alert-warning',
            'info': 'alert-info',
            'debug': 'alert-info'
        };
        // Se a tag não estiver no mapa (ex: 'error'), usa alert-danger
        finalClass = tagMap[providedTag] || `alert-danger`; 
    }

    const alertDiv = document.createElement('div');
    alertDiv.className = `alert ${tags}`;
    alertDiv.setAttribute('role', 'alert');

    let iconName = 'msg-info.svg';
    if (finalClass.includes('success')) iconName = 'msg-suss.svg';
    else if (finalClass.includes('danger')) iconName = 'msg-dang.svg';

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

    messageTimeOut(alertDiv);
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

window.formatMoney = (value) => {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
};