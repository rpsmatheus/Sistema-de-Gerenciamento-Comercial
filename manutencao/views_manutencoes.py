"""Páginas de manutenções: /manutencao/..."""
from datetime import date

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Sum
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from core.mixins import BuscaMixin
from unidades.models import Unidade

from .forms import ManutencaoForm
from .models import Equipamento, Manutencao

# Valor especial do filtro de status: pendentes e em andamento juntas.
EM_ABERTO = 'aberta'


class ManutencaoListaView(LoginRequiredMixin, BuscaMixin, ListView):
    """Histórico de manutenções, com filtros, contagem por status e custo."""

    model = Manutencao
    template_name = 'manutencao/lista.html'
    context_object_name = 'manutencoes'
    paginate_by = 20
    campos_busca = ['descricao', 'equipamento__nome']

    def get_data(self, parametro):
        """Lê uma data da URL no formato AAAA-MM-DD. Inválida vira None."""
        try:
            return date.fromisoformat(self.request.GET.get(parametro, ''))
        except ValueError:
            return None

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'equipamento', 'equipamento__unidade', 'fornecedor',
        )
        parametros = self.request.GET

        equipamento = parametros.get('equipamento', '')
        if equipamento.isdigit():
            queryset = queryset.filter(equipamento_id=equipamento)

        # equipamento__unidade atravessa duas ligações: manutenção ->
        # equipamento -> unidade.
        unidade = parametros.get('unidade', '')
        if unidade.isdigit():
            queryset = queryset.filter(equipamento__unidade_id=unidade)

        status = parametros.get('status', '')
        if status == EM_ABERTO:
            queryset = queryset.exclude(status=Manutencao.Status.CONCLUIDA)
        elif status in Manutencao.Status.values:
            queryset = queryset.filter(status=status)

        tipo = parametros.get('tipo', '')
        if tipo in Manutencao.Tipo.values:
            queryset = queryset.filter(tipo=tipo)

        inicio = self.get_data('de')
        if inicio:
            queryset = queryset.filter(data__gte=inicio)

        fim = self.get_data('ate')
        if fim:
            queryset = queryset.filter(data__lte=fim)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filtrados = self.object_list

        # Custo total e quantidade de manutenções de TODAS as páginas.
        resumo = filtrados.aggregate(custo=Sum('custo'), quantidade=Count('pk'))
        context['custo_total'] = resumo['custo'] or 0
        context['quantidade'] = resumo['quantidade']

        # Quantas manutenções há em cada status, dentro do filtro atual.
        por_status = dict(
            filtrados.order_by().values_list('status').annotate(total=Count('pk'))
        )
        context['por_status'] = [
            (valor, rotulo, por_status.get(valor, 0))
            for valor, rotulo in Manutencao.Status.choices
        ]

        parametros = self.request.GET
        context['equipamentos'] = Equipamento.objects.select_related('unidade')
        context['unidades'] = Unidade.objects.all()
        context['status_opcoes'] = [(EM_ABERTO, 'Em aberto')] + list(Manutencao.Status.choices)
        context['tipos'] = Manutencao.Tipo.choices
        for nome in ['equipamento', 'unidade', 'status', 'tipo', 'de', 'ate']:
            context[f'{nome}_selecionado'] = parametros.get(nome, '')
        context['filtrando'] = bool(context['q']) or any(
            context[f'{nome}_selecionado'] for nome in ['equipamento', 'unidade', 'status', 'tipo', 'de', 'ate']
        )
        return context


class ManutencaoCriarView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Registro de uma nova manutenção."""

    model = Manutencao
    form_class = ManutencaoForm
    template_name = 'manutencao/form.html'
    success_url = reverse_lazy('manutencao_lista')
    success_message = 'Manutenção registrada com sucesso.'

    def get_initial(self):
        # Vindo da lista de equipamentos (?equipamento=3), o formulário já
        # abre com o equipamento escolhido.
        initial = super().get_initial()
        equipamento = self.request.GET.get('equipamento', '')
        if equipamento.isdigit():
            initial['equipamento'] = equipamento
        return initial


class ManutencaoEditarView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Edição de uma manutenção, por exemplo para mudar o status e o custo."""

    model = Manutencao
    form_class = ManutencaoForm
    template_name = 'manutencao/form.html'
    success_url = reverse_lazy('manutencao_lista')
    success_message = 'Manutenção atualizada com sucesso.'


class ManutencaoExcluirView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """Confirmação e remoção de uma manutenção."""

    model = Manutencao
    template_name = 'cadastros/confirmar_exclusao.html'
    success_url = reverse_lazy('manutencao_lista')
    success_message = 'Manutenção removida com sucesso.'
    extra_context = {'url_cancelar': reverse_lazy('manutencao_lista')}
