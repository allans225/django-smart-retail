// TO DO:
/*  
Menu Mobile: A lógica de abrir e fechar o menu lateral em celulares.

Header Fixo (Sticky): Fazer o menu "grudar" no topo quando o usuário rola a página.

Busca: Validação simples do campo de pesquisa antes de enviar.

Mensagens de Alerta (Toast): Aquelas mensagens de "Item adicionado ao carrinho" que desaparecem sozinhas após alguns segundos.

Contador do Carrinho: Atualizar o número de itens no ícone da sacola sem recarregar a página.
*/

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