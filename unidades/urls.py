from django.urls import path

from . import views

# Rotas e nomes seguem o padrão descrito em docs/rotas.md.
urlpatterns = [
    path('', views.UnidadeListaView.as_view(), name='unidades_lista'),
    path('novo/', views.UnidadeCriarView.as_view(), name='unidades_criar'),
    path('<int:pk>/editar/', views.UnidadeEditarView.as_view(), name='unidades_editar'),
    path('<int:pk>/excluir/', views.UnidadeExcluirView.as_view(), name='unidades_excluir'),
]
