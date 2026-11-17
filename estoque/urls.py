from django.urls import path

from . import views

# Rotas e nomes seguem o padrão descrito em docs/rotas.md.
urlpatterns = [
    path('', views.ItemListaView.as_view(), name='estoque_lista'),
    path('novo/', views.ItemCriarView.as_view(), name='estoque_criar'),
    path('<int:pk>/editar/', views.ItemEditarView.as_view(), name='estoque_editar'),
    path('<int:pk>/excluir/', views.ItemExcluirView.as_view(), name='estoque_excluir'),
]
