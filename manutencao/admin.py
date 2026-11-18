from django.contrib import admin

from .forms import EquipamentoForm, ManutencaoForm
from .models import Equipamento, Manutencao


@admin.register(Equipamento)
class EquipamentoAdmin(admin.ModelAdmin):
    form = EquipamentoForm
    list_display = ['nome', 'unidade', 'marca_modelo', 'data_aquisicao']
    list_filter = ['unidade']
    search_fields = ['nome', 'marca_modelo']


@admin.register(Manutencao)
class ManutencaoAdmin(admin.ModelAdmin):
    form = ManutencaoForm
    list_display = ['data', 'equipamento', 'tipo', 'status', 'custo', 'fornecedor']
    list_filter = ['status', 'tipo', 'equipamento__unidade']
    search_fields = ['descricao', 'equipamento__nome']
