from django.db import models

from unidades.models import Unidade


class Funcionario(models.Model):
    """Pessoa que trabalha em uma das unidades da empresa."""

    class Cargo(models.TextChoices):
        PADEIRO = 'padeiro', 'Padeiro(a)'
        CONFEITEIRO = 'confeiteiro', 'Confeiteiro(a)'
        AUXILIAR = 'auxiliar', 'Auxiliar de produção'
        ATENDENTE = 'atendente', 'Atendente'
        CAIXA = 'caixa', 'Operador(a) de caixa'
        ENTREGADOR = 'entregador', 'Entregador(a)'
        GERENTE = 'gerente', 'Gerente de unidade'
        OUTRO = 'outro', 'Outro'

    class Situacao(models.TextChoices):
        ATIVO = 'ativo', 'Ativo'
        INATIVO = 'inativo', 'Inativo'

    nome = models.CharField('nome', max_length=150)
    # Todo funcionário pertence a uma unidade. PROTECT impede que uma
    # unidade seja removida enquanto tiver funcionários vinculados.
    unidade = models.ForeignKey(
        Unidade,
        verbose_name='unidade',
        on_delete=models.PROTECT,
        related_name='funcionarios',
    )
    cargo = models.CharField('cargo', max_length=20, choices=Cargo.choices)
    telefone = models.CharField('telefone', max_length=20, blank=True)
    email = models.EmailField('e-mail', blank=True)
    data_admissao = models.DateField('data de admissão')
    situacao = models.CharField(
        'situação',
        max_length=10,
        choices=Situacao.choices,
        default=Situacao.ATIVO,
    )
    criado_em = models.DateTimeField('criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'funcionário'
        verbose_name_plural = 'funcionários'
        ordering = ['nome']

    def __str__(self):
        return self.nome

    @property
    def ativo(self):
        return self.situacao == self.Situacao.ATIVO
