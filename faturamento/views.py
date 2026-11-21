from datetime import date, timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Sum
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from core.mixins import BuscaMixin
from unidades.models import Unidade

from .forms import LancamentoForm
from .models import Lancamento

# Todas as views herdam de LoginRequiredMixin: quem não está autenticado
# é redirecionado para a tela de login.


class LancamentoListaView(LoginRequiredMixin, BuscaMixin, ListView):
    """Lançamentos de faturamento, com filtros e totais do período."""

    model = Lancamento
    template_name = 'faturamento/lista.html'
    context_object_name = 'lancamentos'
    paginate_by = 20
    campos_busca = ['descricao']

    def get_data(self, parametro):
        """Lê uma data da URL no formato AAAA-MM-DD. Inválida vira None."""
        try:
            return date.fromisoformat(self.request.GET.get(parametro, ''))
        except ValueError:
            return None

    def get_queryset(self):
        queryset = super().get_queryset().select_related('unidade')

        unidade = self.request.GET.get('unidade', '')
        if unidade.isdigit():
            queryset = queryset.filter(unidade_id=unidade)

        inicio = self.get_data('de')
        if inicio:
            queryset = queryset.filter(data__gte=inicio)

        fim = self.get_data('ate')
        if fim:
            queryset = queryset.filter(data__lte=fim)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # self.object_list é a listagem já filtrada, com TODAS as páginas,
        # e não só os 20 lançamentos da página atual.
        filtrados = self.object_list

        # aggregate calcula no banco um único resultado para a consulta:
        # aqui, a soma dos valores e a quantidade de lançamentos.
        resumo = filtrados.aggregate(total=Sum('valor'), quantidade=Count('pk'))
        context['total'] = resumo['total'] or 0
        context['quantidade'] = resumo['quantidade']

        # values + annotate agrupa por unidade: um total para cada uma.
        context['totais_por_unidade'] = (
            filtrados.order_by()
            .values('unidade__nome')
            .annotate(total=Sum('valor'), quantidade=Count('pk'))
            .order_by('-total')
        )

        context['unidades'] = Unidade.objects.all()
        context['unidade_selecionada'] = self.request.GET.get('unidade', '')
        context['de'] = self.request.GET.get('de', '')
        context['ate'] = self.request.GET.get('ate', '')
        context['filtrando'] = bool(
            context['q'] or context['unidade_selecionada'] or context['de'] or context['ate']
        )
        context['atalhos'] = self.get_atalhos()
        return context

    def get_atalhos(self):
        """Períodos prontos: este mês e o mês passado."""
        hoje = timezone.localdate()
        inicio_mes = hoje.replace(day=1)
        fim_mes_passado = inicio_mes - timedelta(days=1)
        inicio_mes_passado = fim_mes_passado.replace(day=1)
        return [
            ('Este mês', inicio_mes, hoje),
            ('Mês passado', inicio_mes_passado, fim_mes_passado),
        ]


class LancamentoCriarView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Cadastro de um novo lançamento."""

    model = Lancamento
    form_class = LancamentoForm
    template_name = 'faturamento/form.html'
    success_url = reverse_lazy('faturamento_lista')
    success_message = 'Lançamento cadastrado com sucesso.'


class LancamentoEditarView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Edição de um lançamento existente."""

    model = Lancamento
    form_class = LancamentoForm
    template_name = 'faturamento/form.html'
    success_url = reverse_lazy('faturamento_lista')
    success_message = 'Lançamento atualizado com sucesso.'


class LancamentoExcluirView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """Confirmação e remoção de um lançamento."""

    model = Lancamento
    template_name = 'cadastros/confirmar_exclusao.html'
    success_url = reverse_lazy('faturamento_lista')
    success_message = 'Lançamento removido com sucesso.'
    extra_context = {'url_cancelar': reverse_lazy('faturamento_lista')}
