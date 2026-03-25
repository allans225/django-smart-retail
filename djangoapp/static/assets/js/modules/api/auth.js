export const AuthAPI = {
    async postAuth(url, formData) {
        return await getPostData(url, formData);
    }
};

function getCsrf() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

async function getPostData(url, formData) {
    try {
        const response = await fetch(url, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCsrf(),
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        const data = await response.json();

        if (!response.ok) {
            throw {
                status: response.status,
                message: data.message || 'Falha na comunicação com o servidor',
                errors: data.errors || null, 
                tags: data.tags || 'alert-danger'
            };
        }
        return data;
    } catch (error) {
        // Se for um erro de rede (fetch falhou antes do json)
        if (!error.status) {
            error.message = "Erro de conexão com o servidor.";
            error.tags = "alert-danger";
        }
        throw error;
    }
}