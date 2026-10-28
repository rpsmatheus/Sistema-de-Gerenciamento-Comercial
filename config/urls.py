"""Rotas principais do projeto.

Cada app tem o seu próprio urls.py, que é incluído aqui.
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('unidades/', include('unidades.urls')),
    path('clientes/', include('clientes.urls')),
    path('fornecedores/', include('fornecedores.urls')),
    path('funcionarios/', include('funcionarios.urls')),
]
