from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from clientes.models import Cliente


class BuscaDeClientesTests(TestCase):
    def setUp(self):
        usuario = get_user_model().objects.create_user(
            username='gerente',
            password='senha-de-teste-123',
        )
        self.client.force_login(usuario)
        Cliente.objects.create(nome='Maria Souza', documento='12345678901', email='maria@exemplo.com')
        Cliente.objects.create(nome='Café da Praça', documento='98765432000155')

    def nomes(self, resposta):
        return [cliente.nome for cliente in resposta.context['clientes']]

    def test_lista_mostra_campo_de_busca(self):
        resposta = self.client.get(reverse('clientes_lista'))
        self.assertContains(resposta, 'name="q"')

    def test_busca_por_nome(self):
        resposta = self.client.get(reverse('clientes_lista'), {'q': 'praça'})
        self.assertEqual(self.nomes(resposta), ['Café da Praça'])

    def test_busca_por_email(self):
        resposta = self.client.get(reverse('clientes_lista'), {'q': 'maria@'})
        self.assertEqual(self.nomes(resposta), ['Maria Souza'])

    def test_busca_por_documento_com_pontuacao(self):
        resposta = self.client.get(reverse('clientes_lista'), {'q': '123.456.789'})
        self.assertEqual(self.nomes(resposta), ['Maria Souza'])

    def test_busca_sem_resultado_mostra_aviso(self):
        resposta = self.client.get(reverse('clientes_lista'), {'q': 'inexistente'})
        self.assertContains(resposta, 'Nenhum cliente encontrado para')
