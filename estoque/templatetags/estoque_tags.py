"""Filtros de template do estoque.

Uso, no topo de um template:
    {% load estoque_tags %}

e depois:
    {{ item.quantidade|quantidade }}   ->  12,5
"""
from django import template

from estoque.formatos import formatar_quantidade

register = template.Library()


@register.filter
def quantidade(valor):
    if valor in (None, ''):
        return ''
    return formatar_quantidade(valor)
