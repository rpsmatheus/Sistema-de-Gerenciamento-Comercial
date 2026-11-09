from django.contrib import admin

from .forms import FornecedorForm
from .models import Fornecedor


@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    form = FornecedorForm
    list_display = ['razao_social', 'nome_fantasia', 'cnpj_formatado', 'contato', 'telefone']
    search_fields = ['razao_social', 'nome_fantasia', 'cnpj', 'contato']

    @admin.display(description='CNPJ')
    def cnpj_formatado(self, fornecedor):
        return fornecedor.cnpj_formatado
