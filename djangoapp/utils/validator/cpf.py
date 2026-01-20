import re

def validate_cpf(cpf):
    # Limpa o CPF mantendo apenas números
    cpf = re.sub(r'[^0-9]', '', str(cpf))

    # Verifica tamanho e se é uma sequência repetida
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    # Cálculo dos dois dígitos verificadores
    def calcular_digito(fatia_cpf):
        multiplicador = len(fatia_cpf) + 1
        soma = sum(int(digito) * m for digito, m in zip(fatia_cpf, range(multiplicador, 1, -1)))
        
        resto = soma % 11
        return '0' if resto < 2 else str(11 - resto)

    # Valida o primeiro dígito
    digito_1 = calcular_digito(cpf[:9])
    if digito_1 != cpf[9]:
        return False

    # Valida o segundo dígito (usando os 9 originais + o primeiro calculado)
    digito_2 = calcular_digito(cpf[:10])
    if digito_2 != cpf[10]:
        return False

    return True
    