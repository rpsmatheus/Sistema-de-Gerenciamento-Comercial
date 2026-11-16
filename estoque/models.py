from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from fornecedores.models import Fornecedor
from unidades.models import Unidade


class ItemEstoque(models.Model):
    """Um produto ou insumo guardado em uma unidade.

    A quantidade NÃO é editada diretamente: ela só muda quando uma
    movimentação (entrada ou saída) é registrada. Assim, o histórico de
    movimentações sempre explica o saldo atual.
    """

    class Tipo(models.TextChoices):
        INSUMO = 'insumo', 'Insumo'
        PRODUTO = 'produto', 'Produto'

    class UnidadeMedida(models.TextChoices):
        KG = 'kg', 'Quilograma (kg)'
        G = 'g', 'Grama (g)'
        L = 'L', 'Litro (L)'
        ML = 'ml', 'Mililitro (ml)'
        UN = 'un', 'Unidade (un)'
        PCT = 'pct', 'Pacote (pct)'
        CX = 'cx', 'Caixa (cx)'

    nome = models.CharField('nome', max_length=100)
    tipo = models.CharField('tipo', max_length=10, choices=Tipo.choices)
    unidade_medida = models.CharField(
        'unidade de medida', max_length=5, choices=UnidadeMedida.choices,
    )
    # Todo item fica em uma unidade da empresa. PROTECT impede remover
    # uma unidade que ainda tenha itens de estoque.
    unidade = models.ForeignKey(
        Unidade,
        verbose_name='unidade',
        on_delete=models.PROTECT,
        related_name='itens_estoque',
    )
    # O fornecedor é opcional. SET_NULL faz o item continuar existindo,
    # sem fornecedor, se o fornecedor for removido.
    fornecedor = models.ForeignKey(
        Fornecedor,
        verbose_name='fornecedor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='itens_estoque',
    )
    quantidade = models.DecimalField(
        'quantidade em estoque', max_digits=10, decimal_places=3, default=Decimal('0'),
    )
    quantidade_minima = models.DecimalField(
        'quantidade mínima',
        max_digits=10,
        decimal_places=3,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
        help_text='Abaixo ou igual a este valor, o item aparece com alerta de estoque baixo.',
    )
    criado_em = models.DateTimeField('criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'item de estoque'
        verbose_name_plural = 'itens de estoque'
        ordering = ['nome', 'unidade__nome']
        constraints = [
            # O mesmo item não pode ser cadastrado duas vezes na mesma unidade.
            models.UniqueConstraint(
                fields=['nome', 'unidade'],
                name='item_unico_por_unidade',
                violation_error_message='Este item já está cadastrado nesta unidade.',
            ),
            # Última barreira contra estoque negativo, no próprio banco.
            models.CheckConstraint(
                condition=models.Q(quantidade__gte=0),
                name='quantidade_nao_negativa',
            ),
        ]

    def __str__(self):
        return f'{self.nome} ({self.unidade})'

    @property
    def estoque_baixo(self):
        return self.quantidade <= self.quantidade_minima


class Movimentacao(models.Model):
    """Uma entrada ou saída de um item de estoque."""

    class Tipo(models.TextChoices):
        ENTRADA = 'entrada', 'Entrada'
        SAIDA = 'saida', 'Saída'

    # CASCADE: ao remover um item, o histórico dele é removido junto.
    item = models.ForeignKey(
        ItemEstoque,
        verbose_name='item',
        on_delete=models.CASCADE,
        related_name='movimentacoes',
    )
    tipo = models.CharField('tipo', max_length=10, choices=Tipo.choices)
    quantidade = models.DecimalField(
        'quantidade',
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))],
    )
    # Saldo do item logo depois desta movimentação, para o histórico.
    saldo_apos = models.DecimalField('saldo após', max_digits=10, decimal_places=3)
    data = models.DateTimeField('data', default=timezone.now)
    observacao = models.CharField('observação', max_length=200, blank=True)

    class Meta:
        verbose_name = 'movimentação'
        verbose_name_plural = 'movimentações'
        ordering = ['-data', '-pk']

    def __str__(self):
        return f'{self.get_tipo_display()} de {self.quantidade} {self.item.unidade_medida} — {self.item.nome}'

    @property
    def eh_entrada(self):
        return self.tipo == self.Tipo.ENTRADA
