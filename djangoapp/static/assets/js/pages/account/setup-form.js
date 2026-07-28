import { FormsActions } from '../../modules/api/form-ui-core.js';

const SetupFormsUI = {
    initTabs: () => {
        // Seleciona todos os itens do menu e formulários
        const menuItens = document.querySelectorAll('.menu-setup-block .settings-menu li');
        const forms = document.querySelectorAll('.form-setup-block form');
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

    const basicdataForm = document.getElementById('basicdata-form');
    const addressForm = document.getElementById('address-form');
    const securityForm = document.getElementById('securitydata-form');

    if (basicdataForm)
        basicdataForm.addEventListener('submit', (e) => FormsActions.handleSubmit(e));

    if (addressForm)
        addressForm.addEventListener('submit', (e) => FormsActions.handleSubmit(e));

    if (securityForm)
        securityForm.addEventListener('submit', (e) => FormsActions.handleSubmit(e));
}
init();