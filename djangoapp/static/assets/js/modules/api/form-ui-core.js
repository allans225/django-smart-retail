import { FormCore } from './form-core.js';

const FormsUI = {
    visualChargingFeedback(element, msg = null) {
        if (msg) {
            element.dataset.originalText = element.innerText;
            element.innerText = msg;
            element.disabled = true;
        } else {
            element.innerText = element.dataset.originalText || "Enviar";
            element.disabled = false;
        }
    },

    // Limpa estados de erro do formulário
    clearErrors(form) {
        form.querySelectorAll('.error-message').forEach(span => {
            span.innerText = '';
            span.style.display = 'none';
        });
        form.querySelectorAll('.auth-input').forEach(input => input.classList.remove('input-error'));
    },

    // Verifica se existem erros específicos por campo vindos do servidor
    renderFieldErrors(form, errors) {
        Object.keys(errors).forEach(fieldName => {

            // Trata o erro global "__all__" jogando para o showAlert
            if (fieldName === '__all__') {
                const globalMessage = errors['__all__'][0].message;
                showAlert(globalMessage, 'alert-danger');
                return; // pula para o próximo campo
            }

            const errorSpan = document.getElementById(`error-${fieldName}`);
            const inputField = form.querySelector(`[name="${fieldName}"]`);

            if (errorSpan) {
                // O get_json_data() do django, enviando uma lista de objs
                const message = errors[fieldName][0].message || errors[fieldName][0];
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
}

export const FormsActions = {
    async handleSubmit(e) {
        e.preventDefault();
        const form = e.target;

        FormsUI.clearErrors(form);

        const submitBtn = form.querySelector('button[type="submit"]');
        const url = form.getAttribute('data-url');
        const formData = new FormData(form);

        FormsUI.visualChargingFeedback(submitBtn, "Processando...");

        try {
            const result = await FormCore.post(url, formData);
            if (result.status === 'success'){
                // se houver redirect enviada pelo Dango, redireciona.
                if (result.redirect) {
                    window.location.href = result.redirect;
                } else {
                    // se não houver, mostra a mensagem
                    FormsUI.visualChargingFeedback(submitBtn);
                    showAlert(result.message || 'Dados salvos com sucesso!', result.tags || 'alert-success');
                }
            }
        } catch (error) {
            // Reativa o botão em caso de erro
            FormsUI.visualChargingFeedback(submitBtn);
            console.log("Objeto de erro capturado:", error);
            if (error.errors) {
                FormsUI.renderFieldErrors(form, error.errors);
            }
            // Mostra apenas o alert geral se não for um erro específico de campo ou se for um erro principal
            if(error.message && !error.errors)
                showAlert(error.message, 'alert-danger')
        }
    },
};