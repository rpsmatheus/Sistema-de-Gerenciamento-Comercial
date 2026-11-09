from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import ProtectedError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import UnidadeForm
from .models import Unidade

# Todas as views herdam de LoginRequiredMixin: quem não está autenticado
# é redirecionado para a tela de login.


class UnidadeListaView(LoginRequiredMixin, ListView):
    """Listagem das unidades, com 10 por página."""

    model = Unidade
    template_name = 'unidades/lista.html'
    context_object_name = 'unidades'
    paginate_by = 10


class UnidadeCriarView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Formulário de cadastro de uma nova unidade."""

    model = Unidade
    form_class = UnidadeForm
    template_name = 'unidades/form.html'
    success_url = reverse_lazy('unidades_lista')
    success_message = 'Unidade cadastrada com sucesso.'


class UnidadeEditarView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Formulário de edição de uma unidade existente."""

    model = Unidade
    form_class = UnidadeForm
    template_name = 'unidades/form.html'
    success_url = reverse_lazy('unidades_lista')
    success_message = 'Unidade atualizada com sucesso.'


class UnidadeExcluirView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """Página de confirmação e remoção de uma unidade."""

    model = Unidade
    template_name = 'cadastros/confirmar_exclusao.html'
    success_url = reverse_lazy('unidades_lista')
    success_message = 'Unidade removida com sucesso.'
    extra_context = {'url_cancelar': reverse_lazy('unidades_lista')}

    def form_valid(self, form):
        # Uma unidade com funcionários vinculados não pode ser removida
        # (o model Funcionario usa on_delete=PROTECT). Em vez de mostrar
        # uma página de erro, o sistema volta para a listagem com um aviso.
        try:
            return super().form_valid(form)
        except ProtectedError:
            messages.error(
                self.request,
                f'A unidade "{self.object}" não pode ser removida porque tem '
                'funcionários vinculados. Transfira ou remova os funcionários antes.',
            )
            return redirect('unidades_lista')
