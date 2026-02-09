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