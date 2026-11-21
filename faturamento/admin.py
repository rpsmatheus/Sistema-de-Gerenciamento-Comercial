from django.contrib import admin

from .forms import LancamentoForm
from .models import Lancamento


@admin.register(Lancamento)
class LancamentoAdmin(admin.ModelAdmin):
    form = LancamentoForm
    list_display = ['data', 'unidade', 'descricao', 'valor']
    list_filter = ['unidade']
    search_fields = ['descricao']
    date_hierarchy = 'data'
