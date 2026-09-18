import { FormCore } from '../../modules/api/form-core.js';
import { FormsActions, Masks } from '../../modules/api/form-ui-core.js';
import { AddressActions } from '../../modules/api/address.js';

const ProfilePictureActions = {
    async listenRemoveBtn(element) {
        if (element) {
            element.addEventListener('click', async (e) => {
                if (!confirm('Tem certeza que deseja remover sua foto de perfil?')) return;

                const url = element.getAttribute('data-url');
                const originalText = element.innerText;

                element.innerText = 'Removendo...';
                element.disabled = true;
                try {
                    // reaproveitando o FormCore passando um FormData vazio
                    const result = await FormCore.post(url, new FormData());

                    if (result.status === 'success') {
                        window.location.reload();
                    }
                } catch (error) {
                    element.innerText = originalText;
                    element.disabled = false;

                    if (window.showAlert) {
                        showAlert(
                            error.message || 'Erro ao remover foto.', 
                            error.tags || 'alert-danger'
                        );
                    }
                }
            });
        }
    }
}

const init = () => {
    Masks.init();
    // Aplica a máscara de CPF aos campos existentes com o valor já preenchido do banco de dados
    document.querySelectorAll('[data-mask="cpf"]').forEach(input => {
        if (input.value)
            input.value = Masks.cpf(input.value);
    });
    // Aplica a máscara de CEP aos campos existentes com o valor já preenchido do banco de dados
    document.querySelectorAll('[data-mask="cep"]').forEach(input => {
        if (input.value)
            input.value = Masks.cep(input.value);
    });
    
    const basicdataForm = document.getElementById('basicdata-form');
    const addressForm = document.getElementById('address-form');
    const securityForm = document.getElementById('securitydata-form');
    const profilePictureForm = document.getElementById('profile-picture-form');
    const btnRemovePicture = document.getElementById('btn-remove-picture');
    const zipInput = document.querySelector('[name="zip_code"]');

    if (basicdataForm)
        basicdataForm.addEventListener('submit', (e) => FormsActions.handleSubmit(e));
    
    if (addressForm)
        addressForm.addEventListener('submit', (e) => FormsActions.handleSubmit(e));

    if (securityForm)
        securityForm.addEventListener('submit', (e) => FormsActions.handleSubmit(e));

    if (zipInput)
        zipInput.addEventListener('input', (e) => AddressActions.handleCepLocup(e));

    if (profilePictureForm)
        profilePictureForm.addEventListener('submit', (e) => FormsActions.handleSubmit(e));

    ProfilePictureActions.listenRemoveBtn(btnRemovePicture);
}
init();