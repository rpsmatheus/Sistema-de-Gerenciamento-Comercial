from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.views.generic import ListView

from core.mixins import BuscaMixin


class AutenticacaoTests(TestCase):
    """Testes de login, logout e proteção das páginas."""

    @classmethod
    def setUpTestData(cls):
        cls.usuario = get_user_model().objects.create_user(
            username='gerente',
            password='senha-de-teste-123',
        )

    def test_dashboard_redireciona_visitante_para_o_login(self):
        resposta = self.client.get(reverse('dashboard'))
        self.assertRedirects(resposta, '/login/?next=/')

    def test_pagina_de_login_abre(self):
        resposta = self.client.get(reverse('login'))
        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, 'registration/login.html')

    def test_login_com_dados_corretos_leva_ao_dashboard(self):
        resposta = self.client.post(reverse('login'), {
            'username': 'gerente',
            'password': 'senha-de-teste-123',
        })
        self.assertRedirects(resposta, reverse('dashboard'))

    def test_login_com_senha_errada_mostra_erro(self):
        resposta = self.client.post(reverse('login'), {
            'username': 'gerente',
            'password': 'senha-errada',
        })
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, 'Usuário ou senha incorretos')

    def test_logout_encerra_a_sessao(self):
        self.client.force_login(self.usuario)
        resposta = self.client.post(reverse('logout'))
        self.assertRedirects(resposta, reverse('login'))

        # Depois de sair, o dashboard volta a exigir login.
        resposta = self.client.get(reverse('dashboard'))
        self.assertEqual(resposta.status_code, 302)

    def test_logout_por_get_nao_e_permitido(self):
        self.client.force_login(self.usuario)
        resposta = self.client.get(reverse('logout'))
        self.assertEqual(resposta.status_code, 405)


class DashboardTests(TestCase):
    """Testes do dashboard para um usuário autenticado."""

    def setUp(self):
        usuario = get_user_model().objects.create_user(
            username='gerente',
            password='senha-de-teste-123',
        )
        self.client.force_login(usuario)

    def test_dashboard_responde_com_sucesso(self):
        resposta = self.client.get(reverse('dashboard'))
        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, 'base.html')
        self.assertTemplateUsed(resposta, 'core/dashboard.html')

    def test_dashboard_lista_os_modulos(self):
        resposta = self.client.get(reverse('dashboard'))
        self.assertContains(resposta, 'Estoque')
        self.assertContains(resposta, 'Faturamento')

    def test_menu_mostra_usuario_e_botao_sair(self):
        resposta = self.client.get(reverse('dashboard'))
        self.assertContains(resposta, 'Olá, gerente')
        self.assertContains(resposta, 'Sair')

    def test_modulos_prontos_tem_link_no_dashboard_e_no_menu(self):
        resposta = self.client.get(reverse('dashboard'))
        self.assertContains(resposta, f'href="{reverse("unidades_lista")}"')
        self.assertContains(resposta, f'href="{reverse("clientes_lista")}"')
        self.assertContains(resposta, 'Disponível')


class UsuarioListaView(BuscaMixin, ListView):
    """View usada apenas nos testes do BuscaMixin."""

    model = get_user_model()
    campos_busca = ['username', 'email']
    ordering = ['username']
    paginate_by = 2


class BuscaMixinTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Usuario = get_user_model()
        Usuario.objects.create_user(username='ana', email='ana@exemplo.com')
        Usuario.objects.create_user(username='bruno', email='bruno@padaria.com')
        Usuario.objects.create_user(username='carla', email='carla@padaria.com')

    def resposta(self, parametros):
        request = RequestFactory().get('/', parametros)
        view = UsuarioListaView.as_view(template_name='base.html')
        return view(request)

    def nomes(self, resposta):
        return [usuario.username for usuario in resposta.context_data['object_list']]

    def test_sem_busca_lista_todos(self):
        resposta = self.resposta({})
        self.assertEqual(resposta.context_data['paginator'].count, 3)
        self.assertEqual(resposta.context_data['q'], '')

    def test_busca_em_qualquer_um_dos_campos(self):
        resposta = self.resposta({'q': 'padaria'})
        self.assertEqual(self.nomes(resposta), ['bruno', 'carla'])

    def test_busca_ignora_maiusculas_e_espacos(self):
        resposta = self.resposta({'q': '  ANA  '})
        self.assertEqual(self.nomes(resposta), ['ana'])
        self.assertEqual(resposta.context_data['q'], 'ANA')

    def test_querystring_mantem_busca_e_remove_pagina(self):
        resposta = self.resposta({'q': 'a', 'page': '2', 'situacao': 'ativo'})
        querystring = resposta.context_data['querystring']
        self.assertIn('q=a', querystring)
        self.assertIn('situacao=ativo', querystring)
        self.assertNotIn('page', querystring)
