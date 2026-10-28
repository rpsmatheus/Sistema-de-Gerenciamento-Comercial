from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
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
