from django.urls import path

from . import views

# Rotas e nomes seguem o padrão descrito em docs/rotas.md.
urlpatterns = [
    path('', views.FornecedorListaView.as_view(), name='fornecedores_lista'),
    path('novo/', views.FornecedorCriarView.as_view(), name='fornecedores_criar'),
    path('<int:pk>/editar/', views.FornecedorEditarView.as_view(), name='fornecedores_editar'),
    path('<int:pk>/excluir/', views.FornecedorExcluirView.as_view(), name='fornecedores_excluir'),
]
