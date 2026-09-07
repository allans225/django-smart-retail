import { FormsActions, Masks } from '../../modules/api/form-ui-core.js';
import { AddressActions } from '../../modules/api/address.js';

const SetupFormsUI = {
    initTabs: () => {
        // Seleciona todos os itens do menu e formulários
        const menuItens = document.querySelectorAll('.menu-setup-block .settings-menu li');
        const forms = document.querySelectorAll('.form-setup-block form');

        // Atualiza o cabeçalho do painel com base no item ativo
        const headerTitle = document.getElementById('setup-head-title');
        const headerSubtitle = document.getElementById('setup-head-subtitle');

        // Estado inicial: oculta todos os formulários, exceto o basicdata
        forms.forEach(form => {
            if (form.id !== 'basicdata-form') {
                form.style.display = 'none';
            }
        });
        // Adiciona evento de clique para cada item do menu
        menuItens.forEach(item => {
            item.addEventListener('click', (e) =>{
                e.preventDefault();

                // pega ID do form pelo atributo data-target HTML
                const targetId = item.getAttribute('data-target');
                if (!targetId) return;
                
                // Atualiza o cabeçalho do painel com base no item clicado
                const title = item.getAttribute('data-tittle') || '';
                const subtitle = item.getAttribute('data-subtittle') || '';
                headerTitle.textContent = title;
                headerSubtitle.textContent = subtitle;

                // remove a class active de todos os itens menu
                menuItens.forEach(li => li.classList.remove('active'));

                // adiciona a classe active no item clicado
                item.classList.add('active');

                // ocultar todos os forms
                forms.forEach(form => {
                    form.style.display = 'none';
                })

                // encontra o form correspondente ao clique e o exibe
                const targetForm = document.getElementById(targetId);
                if (targetId) {
                    targetForm.style.display = 'block';
                } else {
                    console.error(`Erro: Formulário com ID '${targetId}' não foi encontrado no HTML!`);
                }
            });
        })
    }
}

const init = () => {
    SetupFormsUI.initTabs();

    // Inicializa a máscara de CPF
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