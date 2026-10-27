from django.db import models


class Unidade(models.Model):
    """Uma unidade (loja ou fábrica) da empresa.

    Funcionários, estoque, faturamento e equipamentos serão ligados
    a uma unidade nas próximas sprints.
    """

    nome = models.CharField('nome', max_length=100, unique=True)
    endereco = models.CharField('endereço', max_length=200)
    telefone = models.CharField('telefone', max_length=20, blank=True)
    criado_em = models.DateTimeField('criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'unidade'
        verbose_name_plural = 'unidades'
        ordering = ['nome']

    def __str__(self):
        return self.nome
