from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from estoque.models import ItemEstoque
from funcionarios.models import Funcionario
from unidades.models import Unidade


class ExclusaoDeUnidadeComFuncionariosTests(TestCase):
    def setUp(self):
        usuario = get_user_model().objects.create_user(
            username='gerente',
            password='senha-de-teste-123',
        )
        self.client.force_login(usuario)
        self.unidade = Unidade.objects.create(nome='Unidade Centro', endereco='Rua A, 10')

    def test_unidade_sem_funcionarios_e_removida(self):
        resposta = self.client.post(
            reverse('unidades_excluir', args=[self.unidade.pk]),
            follow=True,
        )
        self.assertEqual(Unidade.objects.count(), 0)
        self.assertContains(resposta, 'Unidade removida com sucesso.')

    def test_unidade_com_funcionarios_nao_e_removida(self):
        Funcionario.objects.create(
            nome='João Silva',
            unidade=self.unidade,
            cargo=Funcionario.Cargo.PADEIRO,
            data_admissao=date(2025, 3, 1),
        )
        resposta = self.client.post(
            reverse('unidades_excluir', args=[self.unidade.pk]),
            follow=True,
        )
        self.assertRedirects(resposta, reverse('unidades_lista'))
        self.assertEqual(Unidade.objects.count(), 1)
        self.assertContains(resposta, 'não pode ser removida porque tem funcionários ou itens de estoque vinculados')
        self.assertNotContains(resposta, 'Unidade removida com sucesso.')

    def test_unidade_com_itens_de_estoque_nao_e_removida(self):
        ItemEstoque.objects.create(
            nome='Farinha de trigo', tipo='insumo', unidade_medida='kg', unidade=self.unidade,
        )
        resposta = self.client.post(
            reverse('unidades_excluir', args=[self.unidade.pk]),
            follow=True,
        )
        self.assertEqual(Unidade.objects.count(), 1)
        self.assertContains(resposta, 'itens de estoque vinculados')
