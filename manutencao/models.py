from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from fornecedores.models import Fornecedor
from unidades.models import Unidade


class Equipamento(models.Model):
    """Um equipamento de uma unidade: forno, masseira, câmara fria etc."""

    nome = models.CharField('nome', max_length=100)
    # PROTECT: uma unidade com equipamentos não pode ser removida.
    unidade = models.ForeignKey(
        Unidade,
        verbose_name='unidade',
        on_delete=models.PROTECT,
        related_name='equipamentos',
    )
    marca_modelo = models.CharField('marca e modelo', max_length=100, blank=True)
    data_aquisicao = models.DateField('data de aquisição', null=True, blank=True)
    observacoes = models.TextField('observações', blank=True)
    criado_em = models.DateTimeField('criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'equipamento'
        verbose_name_plural = 'equipamentos'
        ordering = ['nome', 'unidade__nome']

    def __str__(self):
        return f'{self.nome} ({self.unidade})'


class Manutencao(models.Model):
    """Uma manutenção preventiva ou corretiva de um equipamento."""

    class Tipo(models.TextChoices):
        PREVENTIVA = 'preventiva', 'Preventiva'
        CORRETIVA = 'corretiva', 'Corretiva'

    class Status(models.TextChoices):
        PENDENTE = 'pendente', 'Pendente'
        EM_ANDAMENTO = 'em_andamento', 'Em andamento'
        CONCLUIDA = 'concluida', 'Concluída'

    # CASCADE: ao remover um equipamento, o histórico dele é removido junto.
    equipamento = models.ForeignKey(
        Equipamento,
        verbose_name='equipamento',
        on_delete=models.CASCADE,
        related_name='manutencoes',
    )
    tipo = models.CharField('tipo', max_length=10, choices=Tipo.choices)
    descricao = models.CharField('descrição', max_length=200)
    data = models.DateField('data')
    custo = models.DecimalField(
        'custo (R$)',
        max_digits=10,
        decimal_places=2,
        default=Decimal('0'),
        validators=[MinValueValidator(Decimal('0'))],
    )
    status = models.CharField(
        'status', max_length=15, choices=Status.choices, default=Status.PENDENTE,
    )
    # Empresa que fez o serviço, se houver. SET_NULL: remover o fornecedor
    # não apaga o histórico de manutenções.
    fornecedor = models.ForeignKey(
        Fornecedor,
        verbose_name='prestador do serviço',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='manutencoes',
    )
    criado_em = models.DateTimeField('criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'manutenção'
        verbose_name_plural = 'manutenções'
        ordering = ['-data', '-pk']

    def __str__(self):
        return f'{self.get_tipo_display()} — {self.equipamento.nome} ({self.data:%d/%m/%Y})'

    @property
    def aberta(self):
        """Pendente ou em andamento, ou seja, ainda não concluída."""
        return self.status != self.Status.CONCLUIDA
