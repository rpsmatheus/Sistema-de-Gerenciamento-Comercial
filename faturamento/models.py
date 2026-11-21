from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from unidades.models import Unidade


class Lancamento(models.Model):
    """Um lançamento de faturamento de uma unidade em uma data."""

    # PROTECT: uma unidade com lançamentos não pode ser removida, para o
    # histórico de faturamento nunca perder a unidade a que pertence.
    unidade = models.ForeignKey(
        Unidade,
        verbose_name='unidade',
        on_delete=models.PROTECT,
        related_name='lancamentos',
    )
    data = models.DateField('data')
    valor = models.DecimalField(
        'valor (R$)',
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    descricao = models.CharField('descrição', max_length=150)
    criado_em = models.DateTimeField('criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'lançamento de faturamento'
        verbose_name_plural = 'lançamentos de faturamento'
        ordering = ['-data', '-pk']

    def __str__(self):
        return f'{self.descricao} — {self.unidade} ({self.data:%d/%m/%Y})'
