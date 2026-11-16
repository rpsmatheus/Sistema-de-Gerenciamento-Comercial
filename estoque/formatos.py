from decimal import Decimal


def formatar_quantidade(valor):
    """Escreve uma quantidade sem zeros sobrando e com vírgula decimal.

    Exemplos: 12.500 vira "12,5"; 30.000 vira "30"; 0.250 vira "0,25".
    """
    texto = f'{Decimal(valor).normalize():f}'
    return texto.replace('.', ',')
