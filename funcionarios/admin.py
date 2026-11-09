from django.contrib import admin

from .forms import FuncionarioForm
from .models import Funcionario


@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    form = FuncionarioForm
    list_display = ['nome', 'cargo', 'unidade', 'situacao', 'data_admissao']
    list_filter = ['unidade', 'cargo', 'situacao']
    search_fields = ['nome', 'email', 'telefone']
