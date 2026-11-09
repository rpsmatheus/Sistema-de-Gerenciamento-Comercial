from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from core.mixins import BuscaMixin
from unidades.models import Unidade

from .forms import FuncionarioForm
from .models import Funcionario

# Todas as views herdam de LoginRequiredMixin: quem não está autenticado
# é redirecionado para a tela de login.


class FuncionarioListaView(LoginRequiredMixin, BuscaMixin, ListView):
    """Listagem dos funcionários, com busca, filtros e 10 por página."""

    model = Funcionario
    template_name = 'funcionarios/lista.html'
    context_object_name = 'funcionarios'
    paginate_by = 10
    campos_busca = ['nome', 'email', 'telefone']

    def get_queryset(self):
        # select_related busca a unidade de cada funcionário na mesma
        # consulta ao banco, em vez de uma consulta por linha da tabela.
        queryset = super().get_queryset().select_related('unidade')

        unidade = self.request.GET.get('unidade', '')
        if unidade.isdigit():
            queryset = queryset.filter(unidade_id=unidade)

        situacao = self.request.GET.get('situacao', '')
        if situacao in Funcionario.Situacao.values:
            queryset = queryset.filter(situacao=situacao)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Opções e valores atuais dos filtros, para montar os <select>.
        context['unidades'] = Unidade.objects.all()
        context['situacoes'] = Funcionario.Situacao.choices
        context['unidade_selecionada'] = self.request.GET.get('unidade', '')
        context['situacao_selecionada'] = self.request.GET.get('situacao', '')
        context['filtrando'] = bool(
            context['q'] or context['unidade_selecionada'] or context['situacao_selecionada']
        )
        return context


class FuncionarioCriarView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Formulário de cadastro de um novo funcionário."""

    model = Funcionario
    form_class = FuncionarioForm
    template_name = 'funcionarios/form.html'
    success_url = reverse_lazy('funcionarios_lista')
    success_message = 'Funcionário cadastrado com sucesso.'


class FuncionarioEditarView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Formulário de edição de um funcionário existente."""

    model = Funcionario
    form_class = FuncionarioForm
    template_name = 'funcionarios/form.html'
    success_url = reverse_lazy('funcionarios_lista')
    success_message = 'Funcionário atualizado com sucesso.'


class FuncionarioExcluirView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """Página de confirmação e remoção de um funcionário."""

    model = Funcionario
    template_name = 'cadastros/confirmar_exclusao.html'
    success_url = reverse_lazy('funcionarios_lista')
    success_message = 'Funcionário removido com sucesso.'
    extra_context = {'url_cancelar': reverse_lazy('funcionarios_lista')}
