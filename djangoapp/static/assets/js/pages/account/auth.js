import { AuthAPI } from '../../modules/api/auth.js'

const FormsUI = {
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
}

const FormsActions = {
    async handleSubmit(e) {
        e.preventDefault();
        const form = e.target;

        // LIMPEZA INICIAL: Remove todos os erros visíveis antes de tentar novamente
        form.querySelectorAll('.error-message').forEach(span => span.innerText = '');
        form.querySelectorAll('.auth-input').forEach(input => input.classList.remove('input-error'));

        const submitBtn = form.querySelector('button[type="submit"]');
        const url = form.getAttribute('data-url');
        const formData = new FormData(form);

        FormsUI.visualChargingFeedback(submitBtn, "Processando...");

        try {
            const result = await AuthAPI.postAuth(url, formData);
            if (result.status === 'success'){
                // redirect da URL enviada pelo Django
                window.location.href = result.redirect;
            }
        } catch (error) {
            // Reativa o botão em caso de erro
            FormsUI.visualChargingFeedback(submitBtn);

            console.log("Objeto de erro capturado:", error) // debug

            // Verifica se existem erros específicos por campo vindos do servidor
            if(error.errors) {
                Object.keys(error.errors).forEach(fieldName => {

                    // Trata o erro global "__all__" jogando para o showAlert
                    if (fieldName === '__all__') {
                        const globalMessage = error.errors['__all__'][0].message;
                        showAlert(globalMessage, 'alert-danger');
                        return; // pula para o próximo campo
                    }

                    const errorSpan = document.getElementById(`error-${fieldName}`);
                    const inputField = form.querySelector(`[name="${fieldName}"]`);

                    if (errorSpan) {
                        // O get_json_data() do django, enviando uma lista de objs
                        const message = error.errors[fieldName][0].message || error.errors[fieldName][0];
                        errorSpan.innerText = message;
                        
                        errorSpan.style.display = 'block';
                        errorSpan.style.maxHeight = 'none';
                        errorSpan.style.opacity = '1';
                        
                        if (inputField) {
                            inputField.classList.add('input-error');
                        }
                    } else {
                        console.warn(`Aviso: Span error-${fieldName} não encontrado no HTML`)
                    }
                });
            }
            // Mostra apenas o alert geral se não for um erro específico de campo ou se for um erro principal
            if(error.message && !error.errors)
                showAlert(error.message, 'alert-danger')
        }
    },
};

const init = () => {
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const btnAddress = document.getElementById('btn-address');
    const authCards = document.querySelectorAll('.auth-card');
    const toggleLinks = document.querySelectorAll('.toggle-link');
    const authInputs = document.querySelectorAll('.auth-input');

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

    toggleLinks.forEach(link => {
        link.addEventListener('click', (e) => FormsUI.switchAuthMode(e));
    });

    // Estado inicial: Garante que apenas o Login apareça
    if (authCards.length > 1) {
        authCards[1].classList.add('hidden');
    }
};

init();