from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import ClienteForm
from .models import Cliente

# Todas as views herdam de LoginRequiredMixin: quem não está autenticado
# é redirecionado para a tela de login.


class ClienteListaView(LoginRequiredMixin, ListView):
    """Listagem dos clientes, com 10 por página."""

    model = Cliente
    template_name = 'clientes/lista.html'
    context_object_name = 'clientes'
    paginate_by = 10


class ClienteCriarView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Formulário de cadastro de um novo cliente."""

    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/form.html'
    success_url = reverse_lazy('clientes_lista')
    success_message = 'Cliente cadastrado com sucesso.'


class ClienteEditarView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Formulário de edição de um cliente existente."""

    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/form.html'
    success_url = reverse_lazy('clientes_lista')
    success_message = 'Cliente atualizado com sucesso.'


class ClienteExcluirView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """Página de confirmação e remoção de um cliente."""

    model = Cliente
    template_name = 'cadastros/confirmar_exclusao.html'
    success_url = reverse_lazy('clientes_lista')
    success_message = 'Cliente removido com sucesso.'
    extra_context = {'url_cancelar': reverse_lazy('clientes_lista')}
