from django.urls import path

from . import views

# Rotas e nomes seguem o padrão descrito em docs/rotas.md.
urlpatterns = [
    path('', views.FuncionarioListaView.as_view(), name='funcionarios_lista'),
    path('novo/', views.FuncionarioCriarView.as_view(), name='funcionarios_criar'),
    path('<int:pk>/editar/', views.FuncionarioEditarView.as_view(), name='funcionarios_editar'),
    path('<int:pk>/excluir/', views.FuncionarioExcluirView.as_view(), name='funcionarios_excluir'),
]
