from django.urls import path

from . import views

# Rotas e nomes seguem o padrão descrito em docs/rotas.md.
urlpatterns = [
    path('', views.ClienteListaView.as_view(), name='clientes_lista'),
    path('novo/', views.ClienteCriarView.as_view(), name='clientes_criar'),
    path('<int:pk>/editar/', views.ClienteEditarView.as_view(), name='clientes_editar'),
    path('<int:pk>/excluir/', views.ClienteExcluirView.as_view(), name='clientes_excluir'),
]
