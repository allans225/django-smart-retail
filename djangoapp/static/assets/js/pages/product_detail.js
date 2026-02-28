import { CartAPI } from '../modules/api/cart.js';

/*
 * UI - Gerencia apenas a manipulação do DOM
 */
const DetailUI = {
    updatePrice(price, promo, hasPromo) {
        const currentPriceEl = document.getElementById('display-price-current');
        const oldPriceEl = document.getElementById('display-price-old');

        // Lógica de Preço
        if (hasPromo) {
            currentPriceEl.innerText = promo;
            oldPriceEl.innerText = price;
            oldPriceEl.style.display = 'inline';
        } else {
            currentPriceEl.innerText = price;
            oldPriceEl.innerText = 'none';
        }
    },

    updateStocInfo(name, stock) {
        const nameEl = document.getElementById('var-name-display');
        const qtyInput = document.getElementById('product-qty');
        const displayStock = document.getElementById('display-stock');
        const availabilityEl = document.getElementById('display-availability');

        if (nameEl) nameEl.innerHTML = name;
        if (displayStock) displayStock.innerText = stock;

        // Atualiza o max do input de quantidade e reseta para 1 se o estoque for menor que a quantidade atual
        if (qtyInput) {
            qtyInput.setAttribute('max', stock);
            if (parseInt(qtyInput.value) > stock) {
                qtyInput.value = stock > 0 ? 1 : 0;
            }
        }

        // Atualiza a disponibilidade
        if (availabilityEl) {
            const isOut = stock <= 0;
            availabilityEl.innerText = isOut ? 'Indisponível' : 'Disponível';
            availabilityEl.className = isOut ? 'text-red' : 'text-blue';
        }
    },

    updateGallery(images) {
        const featuredImg = document.querySelector('.featured-image img');
        const thumbnailsContainer = document.querySelector('.side-thumbnails');

        // Verificação de segurança para evitar erros de DOM
        if (!featuredImg || !thumbnailsContainer || images.length === 0) return;

        featuredImg.src = images[0]; // Atualiza a imagem principal para a capa (ou a primeira do array)
        thumbnailsContainer.innerHTML = ''; // Limpa as miniaturas

        // Reconstrói as miniaturas
        images.forEach((url, index) => {
            const thumb = document.createElement('img');
            thumb.src = url;
            thumb.className = `t-item ${index === 0 ? 'active' : ''}`; // A primeira miniatura é marcada como ativa
            // Evento para trocar a imagem principal ao clicar na miniatura
            thumb.addEventListener('click', () => {
                featuredImg.src = url;
                document.querySelectorAll('.t-item').forEach(t => t.classList.remove('active'));
                thumb.classList.add('active');
            });
            thumbnailsContainer.appendChild(thumb); // Adiciona a miniatura ao container
        });
    }   
}

/*
 * Actions - Gerencia a lógica de negócio e eventos
 */
const DetailActions = {
    selectVariation(element) {
        if (!element) return;

        // visual da lista de variações
        document.querySelectorAll('.v-item').forEach(el => el.classList.remove('active'));
        element.classList.add('active');

        // Extração dos dados da variação selecionada
        const name = element.dataset.name;
        const price = element.dataset.price;
        const promo = element.dataset.promo;
        const hasPromo = element.dataset.hasPromo === 'true'; // Django template renderiza boolean como string, então comparamos com 'true'
        const stock = parseInt(element.dataset.stock) || 0;   // Garantir que seja um número inteiro
        const variationImagesData = element.dataset.images;

        // Atualização da UI
        DetailUI.updatePrice(price, promo, hasPromo);
        DetailUI.updateStocInfo(name, stock);

        // Galeria de imagens: começa sempre com a capa do produto e depois as imagens específicas da variação (se houver)
        const productCover = document.querySelector('.gallery-main-block').dataset.cover;
        let fullGallery = [productCover]; // Começa com a capa
        if (variationImagesData) { 
            // Adiciona as imagens da variação na galeria, filtra para evitar strings vazias
            fullGallery = fullGallery.concat(variationImagesData.split(',').filter(url => url.trim() !== ""));
        }
        DetailUI.updateGallery(fullGallery);
    },

    async handleAddToCart() {
        // Coleta de dados da UI
        const activeVariation = document.querySelector('.v-item.active');
        const qtyInput = document.getElementById('product-qty');
        const apiUrl = document.getElementById('url-add-cart').value;

        // validação básica
        if (!activeVariation || !qtyInput || !apiUrl) {
            return showAlert('Por favor, selecione uma variação.', 'alert-info');
        }

        const variationId = activeVariation.getAttribute('data-id');
        const quantity = qtyInput ? qtyInput.value : 1; // Default para 1 se o input não for encontrado

        try {
            // Chamada à API para adicionar ao carrinho
            const data = await CartAPI.add(variationId, quantity, apiUrl);
            showAlert(data.message, data.tags); // sucesso ou mensagem de erro do servidor

            if (data.status === 'success' && typeof updateCartBadge === 'function') {
                updateCartBadge(data.total_items_count); // Atualiza o contador do carrinho no header
            }
        } catch (error) {
            // Tratamento de erros de rede ou do Django
            const errorMsg = error.status === 404 
                ? 'Rota não encontrada (404). Verifique as URLs.'
                : error.message || 'Falha na comunicação com o servidor.';
            showAlert(errorMsg, error.tags || 'alert-danger');
        }
    }
};

document.addEventListener('DOMContentLoaded', () => {
    // ouvintes de evento (Add to Cart)
    const addToCartBtn = document.querySelector('.btn-add-to-cart');
    if (addToCartBtn) {
        addToCartBtn.addEventListener('click', (e) => {
            e.preventDefault();
            DetailActions.handleAddToCart();
        });
    }

    // Delegação de clique para variações
    const variationList = document.querySelector('.variation-list');
    if (variationList) {
        variationList.addEventListener('click', e => {
            const clickedItem = e.target.closest('.v-item');
            if (clickedItem) DetailActions.selectVariation(clickedItem);
        });
    }
});