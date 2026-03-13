import { AuthAPI } from '../../modules/api/auth.js'

const FormsActions = {
    async handleSubmit(e) {
        e.preventDefault();
        const form = e.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        const url = form.getAttribute('data-url');
        const formData = new FormData(form);

        this.visualChargingFeedback(submitBtn, "Processando...");

        try {
            const result = await AuthAPI.postAuth(url, formData);

            if (result.status === 'success'){
                // redirect da URL enviada pelo Django
                window.location.href = result.redirect;
            }
        } catch (error) {
            // Reativa o botão em caso de erro
            this.visualChargingFeedback(submitBtn);
            showAlert(error.message, error.tags)
        }
    },

    visualChargingFeedback(element, msg = null) {
        if (msg) {
            element.dataset.originalText = element.innerText;
            element.innerText = msg;
            element.disabled = true;
        } else {
            element.innerText = element.dataset.originalText || "Iniciar";
            element.disabled = false;
        }
    },

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
    const loginForm = document.getElementById('login-form');
    const btnAddress = document.getElementById('btn-address');
    const authCards = document.querySelectorAll('.auth-card');
    const toggleLinks = document.querySelectorAll('.toggle-link');

    if (loginForm){
        loginForm.addEventListener('submit', (e) => FormsActions.handleSubmit(e));
    }

    if (btnAddress)
        btnAddress.addEventListener('click', FormsActions.toggleAddress);

    toggleLinks.forEach(link => {
        link.addEventListener('click', (e) => FormsActions.switchAuthMode(e));
    });

    // Estado inicial: Garante que apenas o Login apareça
    if (authCards.length > 1) {
        authCards[1].classList.add('hidden');
    }
};

init();