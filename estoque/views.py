from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import F
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from core.mixins import BuscaMixin
from unidades.models import Unidade

from .forms import ItemEstoqueForm
from .models import ItemEstoque

# Todas as views herdam de LoginRequiredMixin: quem não está autenticado
# é redirecionado para a tela de login.


class ItemListaView(LoginRequiredMixin, BuscaMixin, ListView):
    """Itens em estoque, com busca, filtros e alerta de estoque baixo."""

    model = ItemEstoque
    template_name = 'estoque/lista.html'
    context_object_name = 'itens'
    paginate_by = 10
    campos_busca = ['nome']

    def get_queryset(self):
        queryset = super().get_queryset().select_related('unidade', 'fornecedor')

        unidade = self.request.GET.get('unidade', '')
        if unidade.isdigit():
            queryset = queryset.filter(unidade_id=unidade)

        tipo = self.request.GET.get('tipo', '')
        if tipo in ItemEstoque.Tipo.values:
            queryset = queryset.filter(tipo=tipo)

        # F('quantidade_minima') compara duas colunas da mesma linha:
        # "quantidade menor ou igual à quantidade mínima deste item".
        if self.request.GET.get('baixo') == '1':
            queryset = queryset.filter(quantidade__lte=F('quantidade_minima'))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unidades'] = Unidade.objects.all()
        context['tipos'] = ItemEstoque.Tipo.choices
        context['unidade_selecionada'] = self.request.GET.get('unidade', '')
        context['tipo_selecionado'] = self.request.GET.get('tipo', '')
        context['so_baixo'] = self.request.GET.get('baixo') == '1'
        context['filtrando'] = bool(
            context['q'] or context['unidade_selecionada']
            or context['tipo_selecionado'] or context['so_baixo']
        )
        context['total_baixo'] = ItemEstoque.objects.filter(
            quantidade__lte=F('quantidade_minima'),
        ).count()
        return context


class ItemCriarView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Cadastro de um novo item. O item começa com quantidade zero."""

    model = ItemEstoque
    form_class = ItemEstoqueForm
    template_name = 'estoque/form.html'
    success_url = reverse_lazy('estoque_lista')
    success_message = 'Item "%(nome)s" cadastrado com sucesso. Registre uma entrada para informar a quantidade.'


class ItemEditarView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Edição dos dados de um item. A quantidade não é editada aqui."""

    model = ItemEstoque
    form_class = ItemEstoqueForm
    template_name = 'estoque/form.html'
    success_url = reverse_lazy('estoque_lista')
    success_message = 'Item atualizado com sucesso.'


class ItemExcluirView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """Confirmação e remoção de um item, junto com o seu histórico."""

    model = ItemEstoque
    template_name = 'cadastros/confirmar_exclusao.html'
    success_url = reverse_lazy('estoque_lista')
    success_message = 'Item removido com sucesso.'
    extra_context = {'url_cancelar': reverse_lazy('estoque_lista')}
