
const FormsActions = {
    switchAuthMode(e) {
        if (e) e.preventDefault(); // Previne o pulo da página no link
        const authCards = document.querySelectorAll('.auth-card');
        authCards.forEach(card => {
            card.classList.toggle('hidden');
        });
    },

    toggleAddress() {
        const addressSection = document.getElementById('address-section');
        const arrowIcon = document.getElementById('arrow-icon');
        
        if (!addressSection || !arrowIcon) return; // Segurança caso os IDs mudem

        const isOpen = addressSection.classList.toggle('open');
        
        // Rotação do ícone conforme o estado
        arrowIcon.style.transform = isOpen ? 'rotate(180deg)' : 'rotate(0deg)';
    }
};

const init = () => {
    const btnAddress = document.getElementById('btn-address');
    const authCards = document.querySelectorAll('.auth-card');
    const toggleLinks = document.querySelectorAll('.toggle-link');

    if (btnAddress) {
        btnAddress.addEventListener('click', FormsActions.toggleAddress);
    }

    toggleLinks.forEach(link => {
        link.addEventListener('click', (e) => FormsActions.switchAuthMode(e));
    });

    // Estado inicial: Garante que apenas o Login apareça
    if (authCards.length > 1) {
        authCards[1].classList.add('hidden');
    }
};

init();