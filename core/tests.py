from django.test import TestCase
from django.urls import reverse


class DashboardTests(TestCase):
    def test_dashboard_responde_com_sucesso(self):
        resposta = self.client.get(reverse('dashboard'))
        self.assertEqual(resposta.status_code, 200)

    def test_dashboard_usa_o_template_base(self):
        resposta = self.client.get(reverse('dashboard'))
        self.assertTemplateUsed(resposta, 'base.html')
        self.assertTemplateUsed(resposta, 'core/dashboard.html')

    def test_dashboard_lista_os_modulos(self):
        resposta = self.client.get(reverse('dashboard'))
        self.assertContains(resposta, 'Estoque')
        self.assertContains(resposta, 'Faturamento')
