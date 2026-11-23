from django.urls import path

from . import views_manutencoes as views

# Rotas em /manutencao/, com os nomes de docs/rotas.md.
urlpatterns = [
    path('', views.ManutencaoListaView.as_view(), name='manutencao_lista'),
    path('nova/', views.ManutencaoCriarView.as_view(), name='manutencao_criar'),
    path('<int:pk>/editar/', views.ManutencaoEditarView.as_view(), name='manutencao_editar'),
    path('<int:pk>/excluir/', views.ManutencaoExcluirView.as_view(), name='manutencao_excluir'),
]
