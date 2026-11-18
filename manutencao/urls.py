from django.urls import include, path

# O módulo tem duas partes, cada uma com o seu arquivo de rotas, para que
# duas pessoas possam trabalhar nelas ao mesmo tempo sem conflito:
#   /manutencao/equipamentos/...  ->  urls_equipamentos.py
#   /manutencao/...               ->  urls_manutencoes.py
urlpatterns = [
    path('equipamentos/', include('manutencao.urls_equipamentos')),
    path('', include('manutencao.urls_manutencoes')),
]
