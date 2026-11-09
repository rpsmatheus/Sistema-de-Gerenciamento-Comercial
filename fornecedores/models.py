from django.db import models


class Fornecedor(models.Model):
    """Empresa que fornece insumos, embalagens ou serviços à padaria."""

    razao_social = models.CharField('razão social', max_length=150)
    nome_fantasia = models.CharField('nome fantasia', max_length=150, blank=True)
    # Guardado somente com números: 14 dígitos.
    cnpj = models.CharField('CNPJ', max_length=14, unique=True)
    contato = models.CharField('pessoa de contato', max_length=100, blank=True)
    telefone = models.CharField('telefone', max_length=20, blank=True)
    email = models.EmailField('e-mail', blank=True)
    observacoes = models.TextField('observações', blank=True)
    criado_em = models.DateTimeField('criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'fornecedor'
        verbose_name_plural = 'fornecedores'
        ordering = ['razao_social']

    def __str__(self):
        return self.nome_fantasia or self.razao_social

    @property
    def cnpj_formatado(self):
        """Retorna o CNPJ com pontuação, para exibir nas telas."""
        c = self.cnpj
        if len(c) == 14:
            return f'{c[:2]}.{c[2:5]}.{c[5:8]}/{c[8:12]}-{c[12:]}'
        return c
