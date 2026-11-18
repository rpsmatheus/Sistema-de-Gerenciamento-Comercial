"""Filtros de template usados em todo o sistema.

Uso, no topo de um template:
    {% load core_tags %}

e depois:
    {{ lancamento.valor|moeda }}   ->  R$ 1.234,56
"""
from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()


def formatar_moeda(valor):
    """Escreve um valor em reais: 1234.5 vira "R$ 1.234,50"."""
    try:
        valor = Decimal(valor).quantize(Decimal('0.01'))
    except (InvalidOperation, TypeError, ValueError):
        return ''
    # O Python formata como 1,234.50; as trocas deixam no padrão brasileiro.
    texto = f'{abs(valor):,.2f}'.replace(',', '#').replace('.', ',').replace('#', '.')
    sinal = '-' if valor < 0 else ''
    return f'{sinal}R$ {texto}'


@register.filter
def moeda(valor):
    if valor in (None, ''):
        return ''
    return formatar_moeda(valor)
