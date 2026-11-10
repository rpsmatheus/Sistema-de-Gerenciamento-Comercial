from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from unidades.models import Unidade


class BuscaDeUnidadesTests(TestCase):
    def setUp(self):
        usuario = get_user_model().objects.create_user(
            username='gerente',
            password='senha-de-teste-123',
        )
        self.client.force_login(usuario)
        Unidade.objects.create(nome='Unidade Centro', endereco='Rua das Padarias, 100')
        Unidade.objects.create(nome='Fábrica', endereco='Distrito Industrial')

    def nomes(self, resposta):
        return [unidade.nome for unidade in resposta.context['unidades']]

    def test_lista_mostra_campo_de_busca(self):
        resposta = self.client.get(reverse('unidades_lista'))
        self.assertContains(resposta, 'name="q"')

    def test_busca_por_nome(self):
        resposta = self.client.get(reverse('unidades_lista'), {'q': 'centro'})
        self.assertEqual(self.nomes(resposta), ['Unidade Centro'])

    def test_busca_por_endereco(self):
        resposta = self.client.get(reverse('unidades_lista'), {'q': 'industrial'})
        self.assertEqual(self.nomes(resposta), ['Fábrica'])

    def test_busca_sem_resultado_mostra_aviso(self):
        resposta = self.client.get(reverse('unidades_lista'), {'q': 'inexistente'})
        self.assertContains(resposta, 'Nenhuma unidade encontrada para')
        self.assertContains(resposta, 'Limpar busca')
