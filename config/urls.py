"""Rotas principais do projeto.

Cada app tem o seu próprio urls.py, que é incluído aqui.
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]
