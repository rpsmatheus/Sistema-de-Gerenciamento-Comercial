from django.db import models


class Cliente(models.Model):
    """Um cliente da empresa, pessoa física ou jurídica."""

    nome = models.CharField('nome', max_length=150)
    # Guardado somente com números: 11 dígitos (CPF) ou 14 dígitos (CNPJ).
    documento = models.CharField('CPF ou CNPJ', max_length=14, unique=True)
    telefone = models.CharField('telefone', max_length=20, blank=True)
    email = models.EmailField('e-mail', blank=True)
    endereco = models.CharField('endereço', max_length=200, blank=True)
    criado_em = models.DateTimeField('criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'cliente'
        verbose_name_plural = 'clientes'
        ordering = ['nome']

    def __str__(self):
        return self.nome

    @property
    def tipo_documento(self):
        """Retorna 'CPF' ou 'CNPJ', conforme a quantidade de dígitos."""
        return 'CNPJ' if len(self.documento) == 14 else 'CPF'

    @property
    def documento_formatado(self):
        """Retorna o documento com pontuação, para exibir nas telas."""
        d = self.documento
        if len(d) == 11:
            return f'{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:]}'
        if len(d) == 14:
            return f'{d[:2]}.{d[2:5]}.{d[5:8]}/{d[8:12]}-{d[12:]}'
        return d
