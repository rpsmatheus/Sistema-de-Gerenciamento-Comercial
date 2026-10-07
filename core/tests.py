from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


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
