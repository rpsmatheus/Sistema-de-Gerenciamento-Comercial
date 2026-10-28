from django.db.models import Q


class BuscaMixin:
    """Adiciona busca por texto a uma ListView.

    Uso:
        class ClienteListaView(LoginRequiredMixin, BuscaMixin, ListView):
            campos_busca = ['nome', 'email']

    O termo digitado chega pela URL, no parâmetro "q" (exemplo:
    /clientes/?q=maria). A listagem mostra os registros em que QUALQUER
    um dos campos de campos_busca contém o termo, sem diferenciar
    maiúsculas de minúsculas.

    O mixin também coloca no contexto do template:
        q            o termo buscado, para preencher o campo de busca
        querystring  os parâmetros da URL sem "page", para a paginação
                     manter a busca e os filtros ao trocar de página
    """

    campos_busca = []

    def get_termo_busca(self):
        return self.request.GET.get('q', '').strip()

    def filtro_busca(self, termo):
        """Monta o filtro da busca. Pode ser sobrescrito em cada view."""
        filtro = Q()
        for campo in self.campos_busca:
            filtro |= Q(**{f'{campo}__icontains': termo})
        return filtro

    def get_queryset(self):
        queryset = super().get_queryset()
        termo = self.get_termo_busca()
        if termo:
            queryset = queryset.filter(self.filtro_busca(termo))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.get_termo_busca()

        parametros = self.request.GET.copy()
        parametros.pop('page', None)
        context['querystring'] = parametros.urlencode()
        return context
