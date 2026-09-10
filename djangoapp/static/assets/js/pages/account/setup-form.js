import { FormsActions, Masks } from '../../modules/api/form-ui-core.js';
import { AddressActions } from '../../modules/api/address.js';

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
    
    const zipInput = document.querySelector('[name="zip_code"]');
    
    if (basicdataForm)
        basicdataForm.addEventListener('submit', (e) => FormsActions.handleSubmit(e));
    
    if (addressForm)
        addressForm.addEventListener('submit', (e) => FormsActions.handleSubmit(e));

    if (securityForm)
        securityForm.addEventListener('submit', (e) => FormsActions.handleSubmit(e));

    if (zipInput)
        zipInput.addEventListener('input', (e) => AddressActions.handleCepLocup(e));
}
init();