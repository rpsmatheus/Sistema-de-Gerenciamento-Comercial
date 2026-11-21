from django.urls import path

from . import views

# Rotas e nomes seguem o padrão descrito em docs/rotas.md.
urlpatterns = [
    path('', views.LancamentoListaView.as_view(), name='faturamento_lista'),
    path('novo/', views.LancamentoCriarView.as_view(), name='faturamento_criar'),
    path('<int:pk>/editar/', views.LancamentoEditarView.as_view(), name='faturamento_editar'),
    path('<int:pk>/excluir/', views.LancamentoExcluirView.as_view(), name='faturamento_excluir'),
]
