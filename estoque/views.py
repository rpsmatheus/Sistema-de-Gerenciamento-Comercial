from datetime import date

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ValidationError
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, FormView, ListView, UpdateView

from core.mixins import BuscaMixin
from unidades.models import Unidade

from .formatos import formatar_quantidade
from .forms import ItemEstoqueForm, MovimentacaoForm
from .models import ItemEstoque, Movimentacao
from .services import registrar_movimentacao

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


class MovimentarView(LoginRequiredMixin, FormView):
    """Registro de uma entrada ou saída de um item."""

    form_class = MovimentacaoForm
    template_name = 'estoque/movimentar.html'
    success_url = reverse_lazy('estoque_lista')

    def get_item(self):
        # Busca o item uma única vez por requisição. Um item que não
        # existe resulta em "Página não encontrada" (404).
        if not hasattr(self, '_item'):
            self._item = get_object_or_404(
                ItemEstoque.objects.select_related('unidade'), pk=self.kwargs['pk'],
            )
        return self._item

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['item'] = self.get_item()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['item'] = self.get_item()
        return context

    def form_valid(self, form):
        item = self.get_item()
        try:
            # A gravação passa SEMPRE pelo serviço, que confere o saldo de
            # novo, já com a linha do item travada no banco.
            movimentacao = registrar_movimentacao(
                item,
                form.cleaned_data['tipo'],
                form.cleaned_data['quantidade'],
                form.cleaned_data['observacao'],
            )
        except ValidationError as erro:
            form.add_error('quantidade', erro)
            return self.form_invalid(form)

        messages.success(
            self.request,
            f'{movimentacao.get_tipo_display()} de '
            f'{formatar_quantidade(movimentacao.quantidade)} {item.unidade_medida} '
            f'registrada para {item.nome}. Saldo atual: '
            f'{formatar_quantidade(movimentacao.saldo_apos)} {item.unidade_medida}.',
        )
        return redirect(self.get_success_url())


class MovimentacaoListaView(LoginRequiredMixin, BuscaMixin, ListView):
    """Histórico de movimentações, com busca e filtros."""

    model = Movimentacao
    template_name = 'estoque/movimentacoes.html'
    context_object_name = 'movimentacoes'
    paginate_by = 20
    campos_busca = ['item__nome', 'observacao']

    def get_data(self, parametro):
        """Lê uma data da URL no formato AAAA-MM-DD. Inválida vira None."""
        try:
            return date.fromisoformat(self.request.GET.get(parametro, ''))
        except ValueError:
            return None

    def get_queryset(self):
        queryset = super().get_queryset().select_related('item', 'item__unidade')

        item = self.request.GET.get('item', '')
        if item.isdigit():
            queryset = queryset.filter(item_id=item)

        tipo = self.request.GET.get('tipo', '')
        if tipo in Movimentacao.Tipo.values:
            queryset = queryset.filter(tipo=tipo)

        inicio = self.get_data('de')
        if inicio:
            queryset = queryset.filter(data__date__gte=inicio)

        fim = self.get_data('ate')
        if fim:
            queryset = queryset.filter(data__date__lte=fim)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['itens'] = ItemEstoque.objects.select_related('unidade')
        context['tipos'] = Movimentacao.Tipo.choices
        context['item_selecionado'] = self.request.GET.get('item', '')
        context['tipo_selecionado'] = self.request.GET.get('tipo', '')
        context['de'] = self.request.GET.get('de', '')
        context['ate'] = self.request.GET.get('ate', '')
        context['filtrando'] = bool(
            context['q'] or context['item_selecionado'] or context['tipo_selecionado']
            or context['de'] or context['ate']
        )
        return context
