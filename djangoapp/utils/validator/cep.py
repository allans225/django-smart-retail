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
        response = requests.get(url, timeout=5)
        data = response.json()
        return not data.get('erro', False)
    except:
        return False