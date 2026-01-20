import re
import requests # type: ignore

"""
Validação de CEP para uma resposta rápida no Admin
"""
def validate_cep(cep):
    # Mantém apenas números
    cep = re.sub(r'[^0-9]', '', str(cep))

    # Verifica se tem 8 dígitos
    if len(cep) != 8:
        return False
    
    # Bloquear sequências óbvias (ex: 00000000)
    if cep == cep[0] * 8:
        
        return False

    return True

"""
Consulta de API na base dos correios, usar no Frontend 
para preencher o endereço automaticamente para o usuário
"""
def look_up_cep(cep):
    cep_limpo = re.sub(r'[^0-9]', '', str(cep))
    url = f"https://viacep.com.br/ws/{cep_limpo}/json/"
    try:
        # Timeout de 2 segundos para não travar o servidor se a API demorar
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            data = response.json()
            # não retorna False (erro) se status code = 200
            return not data.get('erro', False)
    except (requests.exceptions.RequestException, requests.exceptions.Timeout):
        # Se a API falhar, permitimos passar apenas pelo formato (8 dígitos) 
        # para não impedir o cadastro do cliente por falha externa.
        return True 
    
    return False