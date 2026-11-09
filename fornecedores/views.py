import re

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from core.mixins import BuscaMixin

from .forms import FornecedorForm
from .models import Fornecedor

# Todas as views herdam de LoginRequiredMixin: quem não está autenticado
# é redirecionado para a tela de login.


class FornecedorListaView(LoginRequiredMixin, BuscaMixin, ListView):
    """Listagem dos fornecedores, com busca e 10 por página."""

    model = Fornecedor
    template_name = 'fornecedores/lista.html'
    context_object_name = 'fornecedores'
    paginate_by = 10
    campos_busca = ['razao_social', 'nome_fantasia', 'contato', 'email']

    def filtro_busca(self, termo):
        filtro = super().filtro_busca(termo)
        # O CNPJ é guardado só com números. Assim, buscar "12.345.678"
        # também encontra o fornecedor de CNPJ 12345678000190.
        digitos = re.sub(r'\D', '', termo)
        if digitos:
            filtro |= Q(cnpj__contains=digitos)
        return filtro


class FornecedorCriarView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Formulário de cadastro de um novo fornecedor."""

    model = Fornecedor
    form_class = FornecedorForm
    template_name = 'fornecedores/form.html'
    success_url = reverse_lazy('fornecedores_lista')
    success_message = 'Fornecedor cadastrado com sucesso.'


class FornecedorEditarView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Formulário de edição de um fornecedor existente."""

    model = Fornecedor
    form_class = FornecedorForm
    template_name = 'fornecedores/form.html'
    success_url = reverse_lazy('fornecedores_lista')
    success_message = 'Fornecedor atualizado com sucesso.'


class FornecedorExcluirView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """Página de confirmação e remoção de um fornecedor."""

    model = Fornecedor
    template_name = 'cadastros/confirmar_exclusao.html'
    success_url = reverse_lazy('fornecedores_lista')
    success_message = 'Fornecedor removido com sucesso.'
    extra_context = {'url_cancelar': reverse_lazy('fornecedores_lista')}
