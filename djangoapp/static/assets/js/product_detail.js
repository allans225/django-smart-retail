function changeQty(steps) {
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
}

// Funçao auxiliar para as miniaturas funcionarem antes de qualquer troca de variação do produto
function changeFeatured(element) {
    const featuredImg = document.querySelector('.featured-image img');
    if (featuredImg && element) {
        featuredImg.src = element.src;
        // Atualiza a classe active
        document.querySelectorAll('.t-item').forEach(img => img.classList.remove('active'));
        element.classList.add('active');
    }
}

function selectVariation(element) {
    // Verifica se o elemento existe
    if (!element) {
        console.error('Elemento de variação não encontrado.');
        return;
    }
    // remove a classe ativa de todos
    document.querySelectorAll('.v-item').forEach(el => el.classList.remove('active'));
    // adiciona a classe ativa ao clicado
    element.classList.add('active');

    // Captura os dados do elemento clicado
    const name = element.getAttribute('data-name');
    const price = element.getAttribute('data-price');
    const promo = element.getAttribute('data-promo');
    const hasPromo = element.getAttribute('data-has-promo') === 'true';
    // Sincroniza o estoque do seletor
    const stock = parseInt(element.getAttribute('data-stock')) || 0;
    const qtyInput = document.getElementById('product-qty');
    const displayStock = document.getElementById('display-stock');

    // atualização dos textos na tela
    document.getElementById('var-name-display').innerText = name;
    document.getElementById('display-stock').innerText = stock;

    // capturando os elementos de preço
    const currentPriceEl = document.getElementById('display-price-current');
    const oldPriceEl = document.getElementById('display-price-old');

    if (qtyInput) {
        qtyInput.setAttribute('max', stock);
        // Se a quantidade selecionada for maior que o novo estoque, reseta para o máximo
        if (parseInt(qtyInput.value) > stock) {
            qtyInput.value = stock > 0 ? 1 : 0;
        }
    }

    if (displayStock) {
        displayStock.innerText = stock;
    }

    // Lógica de Preço
    if (hasPromo) {
        currentPriceEl.innerText = promo;
        oldPriceEl.innerText = price;
    } else {
        currentPriceEl.innerText = price;
    }

    // Lógica de Disponibilidade
    const availabilityEl = document.getElementById('display-availability');
    if (stock <= 0) {
        availabilityEl.innerText = 'Indisponível';
        availabilityEl.classList.replace('text-blue', 'text-red');
    } else {
        availabilityEl.innerText = 'Disponível';
        availabilityEl.classList.replace('text-red', 'text-blue');
    }

    // pega a capa global e as imagens da variação
    const productCover = document.querySelector('.gallery-main-block').getAttribute('data-cover');
    const variationImagesData = element.getAttribute('data-images');
    
    // cria o array da galeria começando sempre pela capa
    let fullGallery = [productCover];

    if (variationImagesData) {
        // Filtra para evitar strings vazias caso não haja imagens extras
        const extras = variationImagesData.split(',').filter(url => url.trim() !== "");
        fullGallery = fullGallery.concat(extras);
    }

    updateGalleryUI(fullGallery);
}

async function addToCart() {
    const activeVariation = document.querySelector('.v-item.active');

    if (!activeVariation) {
        showAlert('Por favor, selecione uma variação.', 'alert-info');
        return;
    }

    const variationId = activeVariation.getAttribute('data-id');

    const quantity = document.getElementById('product-qty').value; 
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    const formData = new FormData();
    formData.append('variation_id', variationId);
    formData.append('quantity', quantity);
    formData.append('csrfmiddlewaretoken', csrfToken);

    // Captura a URL gerada pelo Django
    const url = document.getElementById('url-add-cart').value;

    try {
        const response = await fetch(url, {
            method: 'POST',
            body: formData,
            headers: { 'X-Requested-With': 'XMLHttpRequest' } 
        });

        if (response.status === 404) {
            showAlert('Erro: Rota não encontrada (404). Verifique as URLs.', 'alert-danger');
            return;
        }
        
        const data = await response.json();
        showAlert(data.message, data.tags);

        if (data.status === 'success') {
            const cartCounter = document.querySelector('nav .badge');
            if (cartCounter) cartCounter.innerText = data.total_items_count;
            console.log("Conteúdo atual no carrinho (total de itens): ", data.total_items_count);
        }
    } catch (error) {
        showAlert('Falha na comunicação com o servidor.', 'alert-danger');
    }
}

function updateGalleryUI(images) {
    const featuredImg = document.querySelector('.featured-image img');
    const thumbnailsContainer = document.querySelector('.side-thumbnails');

    if (images.length > 0) {
        // Atualiza a imagem principal para a capa (ou a primeira do array)
        featuredImg.src = images[0];

        // Limpa e reconstrói as miniaturas
        thumbnailsContainer.innerHTML = '';
        images.forEach((url, index) => {
            const activeClass = index === 0 ? 'active' : '';
            
            const thumb = document.createElement('img');
            thumb.src = url;
            thumb.className = `t-item ${activeClass}`;
            
            // Evento para trocar a imagem principal ao clicar na miniatura
            thumb.addEventListener('click', function() {
                featuredImg.src = this.src;
                document.querySelectorAll('.t-item').forEach(t => t.classList.remove('active'));
                this.classList.add('active');
            });

            thumbnailsContainer.appendChild(thumb);
        });
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // ouvintes de evento (Add to Cart)
    const addToCartBtn = document.querySelector('.btn-add-to-cart');
    if (addToCartBtn) {
        addToCartBtn.addEventListener('click', (e) => {
            e.preventDefault();
            addToCart();
        });
    }
    
    // Delegação de clique para variações
    const variationList = document.querySelector('.variation-list');
    if (variationList) {
        variationList.addEventListener('click', function(e) {
            const clickedItem = e.target.closest('.v-item');
            if (clickedItem) selectVariation(clickedItem);
        });
    }
});