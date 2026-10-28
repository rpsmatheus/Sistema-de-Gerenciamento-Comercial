from django.contrib import admin

from .forms import ClienteForm
from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    form = ClienteForm
    list_display = ['nome', 'documento_formatado', 'telefone', 'email']
    search_fields = ['nome', 'documento', 'email']

    @admin.display(description='CPF ou CNPJ')
    def documento_formatado(self, cliente):
        return cliente.documento_formatado
