from django.urls import path

from . import views_equipamentos as views

# Rotas em /manutencao/equipamentos/, com os nomes de docs/rotas.md.
urlpatterns = [
    path('', views.EquipamentoListaView.as_view(), name='equipamentos_lista'),
    path('novo/', views.EquipamentoCriarView.as_view(), name='equipamentos_criar'),
    path('<int:pk>/editar/', views.EquipamentoEditarView.as_view(), name='equipamentos_editar'),
    path('<int:pk>/excluir/', views.EquipamentoExcluirView.as_view(), name='equipamentos_excluir'),
]
