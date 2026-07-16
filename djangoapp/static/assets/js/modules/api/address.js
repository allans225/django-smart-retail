export const CepAPI = {
    async fetchAdress(cep){
        const cleanCep = cep.replace(/\D/g, '');
        if (cleanCep.length !== 8 )
            return null;

        try {
            const response = await fetch(`https://viacep.com.br/ws/${cleanCep}/json/`);
            const data = await response.json();

            if (data.erro) return null;
            return data;
        } catch (error) {
            console.error("Erro ao buscar CEP:", error);
            return null;
        }
    }
};

export const AddressActions = {
    async handleCepLocup(e) {
        const zipInput = e.target;
        const cep = e.target.value.replace(/\D/g, '');

        // Encontra o formulário pai para poder buscar outros inputs
        const form = zipInput.closest('form');

        if (cep.length === 8) {
            const inputsToFill = form.querySelectorAll('[name="street"], [name="neighborhood"], [name="city"]');
            inputsToFill.forEach(input => input.placeholder = "Buscando...")
            const address = await CepAPI.fetchAdress(cep);
            inputsToFill.forEach(input => input.placeholder = input.getAttribute('name')); // volta ao placeholder original
            if (address) {
                AddressActions.fillFields(address, form);
            }
        }
    },

    fillFields(data, form) {
        // mapeamento dos campos da API para os names do HTML
        form.querySelector('[name="street"]').value = data.logradouro;
        form.querySelector('[name="neighborhood"]').value = data.bairro;
        form.querySelector('[name="city"]').value = data.localidade;

        // select de Estado (UF)
        const stateSelect = form.querySelector('[name="state"]');
        if (stateSelect) {
            stateSelect.value = data.uf;
        }

        // focus: facilita a continuação do auto preenchimento
        form.querySelector('[name="number"]').focus();
    }
};