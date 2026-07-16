import { FormsActions } from '../../modules/api/form-ui-core.js';
import { AddressActions } from '../../modules/api/address.js';

const FormsUI = {
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
}

const init = () => {
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');

    const btnAddress = document.getElementById('btn-address');
    const authCards = document.querySelectorAll('.auth-card');

    const toggleLinks = document.querySelectorAll('.toggle-link');
    const authInputs = document.querySelectorAll('.auth-input');
    const zipInput = document.querySelector('[name="zip_code"]');
    
    // Limpador: remove a classe de erro assim que o usuário começar a digitar novamente
    if (authInputs.length > 0) {
        authInputs.forEach(input => {
            input.addEventListener('input', () => {
                input.classList.remove('input-error'); // remove borda vermelha
                const errorSpan = document.getElementById(`error-${input.name}`);  // busca o span correspondente
                if (errorSpan) 
                    errorSpan.innerText = ''; // Ao definir como vazio, o CSS (:empty) vai esconder o espaçamento
            });
        });
    }

    if (loginForm)
        loginForm.addEventListener('submit', (e) => FormsActions.handleSubmit(e));

    if (registerForm)
        registerForm.addEventListener('submit', (e) => FormsActions.handleSubmit(e));

    if (btnAddress)
        btnAddress.addEventListener('click', FormsUI.toggleAddress);

    if (zipInput) 
        zipInput.addEventListener('input', (e) => AddressActions.handleCepLocup(e));

    toggleLinks.forEach(link => {
        link.addEventListener('click', (e) => FormsUI.switchAuthMode(e));
    });

    // Estado inicial: Garante que apenas o Login apareça
    if (authCards.length > 1) {
        authCards[1].classList.add('hidden');
    }
};

init();