"""Páginas de equipamentos: /manutencao/equipamentos/..."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from core.mixins import BuscaMixin
from unidades.models import Unidade

from .forms import EquipamentoForm
from .models import Equipamento, Manutencao

# Todas as views herdam de LoginRequiredMixin: quem não está autenticado
# é redirecionado para a tela de login.


class EquipamentoListaView(LoginRequiredMixin, BuscaMixin, ListView):
    """Equipamentos, com busca, filtro por unidade e manutenções em aberto."""

    model = Equipamento
    template_name = 'manutencao/equipamentos/lista.html'
    context_object_name = 'equipamentos'
    paginate_by = 10
    campos_busca = ['nome', 'marca_modelo']

    def get_queryset(self):
        queryset = super().get_queryset().select_related('unidade')

        unidade = self.request.GET.get('unidade', '')
        if unidade.isdigit():
            queryset = queryset.filter(unidade_id=unidade)

        # annotate acrescenta a cada equipamento um campo calculado no banco:
        # quantas manutenções dele ainda não foram concluídas. Consultas com
        # contagem ignoram a ordenação do Meta, por isso o order_by explícito.
        return queryset.annotate(
            em_aberto=Count(
                'manutencoes',
                filter=~Q(manutencoes__status=Manutencao.Status.CONCLUIDA),
            ),
        ).order_by('nome', 'unidade__nome')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unidades'] = Unidade.objects.all()
        context['unidade_selecionada'] = self.request.GET.get('unidade', '')
        context['filtrando'] = bool(context['q'] or context['unidade_selecionada'])
        return context


class EquipamentoCriarView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Cadastro de um novo equipamento."""

    model = Equipamento
    form_class = EquipamentoForm
    template_name = 'manutencao/equipamentos/form.html'
    success_url = reverse_lazy('equipamentos_lista')
    success_message = 'Equipamento cadastrado com sucesso.'


class EquipamentoEditarView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Edição de um equipamento existente."""

    model = Equipamento
    form_class = EquipamentoForm
    template_name = 'manutencao/equipamentos/form.html'
    success_url = reverse_lazy('equipamentos_lista')
    success_message = 'Equipamento atualizado com sucesso.'


class EquipamentoExcluirView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """Confirmação e remoção de um equipamento, junto com o seu histórico."""

    model = Equipamento
    template_name = 'cadastros/confirmar_exclusao.html'
    success_url = reverse_lazy('equipamentos_lista')
    success_message = 'Equipamento removido com sucesso.'
    extra_context = {'url_cancelar': reverse_lazy('equipamentos_lista')}
