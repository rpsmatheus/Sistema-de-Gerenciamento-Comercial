from django.contrib import admin

from .forms import ItemEstoqueForm
from .models import ItemEstoque, Movimentacao


@admin.register(ItemEstoque)
class ItemEstoqueAdmin(admin.ModelAdmin):
    form = ItemEstoqueForm
    list_display = ['nome', 'tipo', 'unidade', 'quantidade', 'unidade_medida', 'quantidade_minima']
    list_filter = ['unidade', 'tipo']
    search_fields = ['nome']


@admin.register(Movimentacao)
class MovimentacaoAdmin(admin.ModelAdmin):
    # O histórico é só para consulta no admin: entradas e saídas devem
    # ser registradas pelo sistema, que atualiza o saldo do item.
    list_display = ['data', 'item', 'tipo', 'quantidade', 'saldo_apos', 'observacao']
    list_filter = ['tipo', 'item__unidade']
    search_fields = ['item__nome', 'observacao']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
