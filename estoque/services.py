"""Regras de negócio do estoque.

Toda entrada ou saída deve passar por registrar_movimentacao. É ela que
garante, em um único lugar, que:

- a quantidade é positiva;
- uma saída nunca deixa o estoque negativo;
- o saldo do item e o histórico de movimentações nunca ficam diferentes.
"""
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction

from .formatos import formatar_quantidade
from .models import ItemEstoque, Movimentacao


def registrar_movimentacao(item, tipo, quantidade, observacao=''):
    """Registra uma entrada ou saída e atualiza o saldo do item.

    Retorna a movimentação criada. Levanta ValidationError, sem alterar
    nada, se a quantidade não for positiva ou se uma saída for maior que
    o saldo disponível.
    """
    quantidade = Decimal(quantidade)
    if quantidade <= 0:
        raise ValidationError('A quantidade deve ser maior que zero.')
    if tipo not in Movimentacao.Tipo.values:
        raise ValidationError('Tipo de movimentação inválido.')

    # transaction.atomic: ou o saldo e o histórico são gravados juntos, ou
    # nenhum dos dois é gravado.
    with transaction.atomic():
        # select_for_update trava a linha do item até o fim da transação.
        # Se duas pessoas registrarem uma saída ao mesmo tempo, a segunda
        # espera a primeira terminar e já enxerga o saldo atualizado.
        item = ItemEstoque.objects.select_for_update().get(pk=item.pk)

        if tipo == Movimentacao.Tipo.SAIDA:
            if quantidade > item.quantidade:
                raise ValidationError(
                    f'Estoque insuficiente: há apenas '
                    f'{formatar_quantidade(item.quantidade)} {item.unidade_medida} '
                    f'de {item.nome} nesta unidade.'
                )
            item.quantidade -= quantidade
        else:
            item.quantidade += quantidade

        item.save(update_fields=['quantidade'])
        return Movimentacao.objects.create(
            item=item,
            tipo=tipo,
            quantidade=quantidade,
            saldo_apos=item.quantidade,
            observacao=observacao.strip(),
        )
