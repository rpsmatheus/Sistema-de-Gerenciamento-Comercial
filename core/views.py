from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

# Módulos do sistema exibidos no dashboard.
# Quando um módulo for implementado, troque "disponivel" para True
# e preencha "url_name" com o nome da rota de listagem dele.
MODULOS = [
    {
        'nome': 'Unidades',
        'descricao': 'Unidades da empresa, usadas pelos demais módulos.',
        'sprint': 2,
        'disponivel': False,
        'url_name': '',
    },
    {
        'nome': 'Clientes',
        'descricao': 'Cadastro e consulta de clientes.',
        'sprint': 2,
        'disponivel': False,
        'url_name': '',
    },
    {
        'nome': 'Fornecedores',
        'descricao': 'Fornecedores, CNPJ e contatos.',
        'sprint': 3,
        'disponivel': False,
        'url_name': '',
    },
    {
        'nome': 'Funcionários',
        'descricao': 'Equipe de cada unidade, cargos e situação.',
        'sprint': 3,
        'disponivel': False,
        'url_name': '',
    },
    {
        'nome': 'Estoque',
        'descricao': 'Produtos, insumos, entradas e saídas.',
        'sprint': 4,
        'disponivel': False,
        'url_name': '',
    },
    {
        'nome': 'Faturamento',
        'descricao': 'Lançamentos de faturamento por unidade.',
        'sprint': 5,
        'disponivel': False,
        'url_name': '',
    },
    {
        'nome': 'Manutenção',
        'descricao': 'Equipamentos e histórico de manutenções.',
        'sprint': 5,
        'disponivel': False,
        'url_name': '',
    },
]


class DashboardView(LoginRequiredMixin, TemplateView):
    """Página inicial do sistema, com atalhos para os módulos.

    O LoginRequiredMixin redireciona para a tela de login quem não
    estiver autenticado. Use o mesmo mixin em todas as views internas.
    """

    template_name = 'core/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['modulos'] = MODULOS
        return context
