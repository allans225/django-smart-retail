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
    const stock = parseInt(element.getAttribute('data-stock'));

    // atualização dos textos na tela
    document.getElementById('var-name-display').innerText = name;
    document.getElementById('display-stock').innerText = stock;

    // capturando os elementos de preço
    const currentPriceEl = document.getElementById('display-price-current');
    const oldPriceEl = document.getElementById('display-price-old');

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

// atribuir o clique via JS quando a página carregar
document.addEventListener('DOMContentLoaded', function() {
    // Container pai das variações
    const variationList = document.querySelector('.variation-list');

    if (variationList) {
        variationList.addEventListener('click', function(e) {
            console.log('Clique detectado na lista de variações. Verificando o alvo:', e.target);
            // Verfica se o que foi clicado é realmente uma variação (v-item)
            const clickedItem = e.target.closest('.v-item');
            
            if (clickedItem) {
                console.log('Variação clicada:', clickedItem.getAttribute('data-name'));
                selectVariation(clickedItem);
            }
        });
    }
});