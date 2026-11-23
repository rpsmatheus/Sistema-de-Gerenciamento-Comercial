from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from manutencao.models import Equipamento, Manutencao
from unidades.models import Unidade


class EquipamentosSemLoginTests(TestCase):
    def test_paginas_redirecionam_para_o_login(self):
        unidade = Unidade.objects.create(nome='Fábrica', endereco='Distrito Industrial')
        forno = Equipamento.objects.create(nome='Forno', unidade=unidade)
        urls = [
            reverse('equipamentos_lista'),
            reverse('equipamentos_criar'),
            reverse('equipamentos_editar', args=[forno.pk]),
            reverse('equipamentos_excluir', args=[forno.pk]),
        ]
        for url in urls:
            with self.subTest(url=url):
                resposta = self.client.get(url)
                self.assertRedirects(resposta, f'/login/?next={url}')


class EquipamentosViewsTests(TestCase):
    def setUp(self):
        usuario = get_user_model().objects.create_user(
            username='gerente',
            password='senha-de-teste-123',
        )
        self.client.force_login(usuario)
        self.fabrica = Unidade.objects.create(nome='Fábrica', endereco='Distrito Industrial')
        self.centro = Unidade.objects.create(nome='Unidade Centro', endereco='Rua A, 10')
        self.forno = Equipamento.objects.create(
            nome='Forno de lastro', unidade=self.fabrica,
            marca_modelo='Lastro 6 esteiras', data_aquisicao=date(2021, 3, 10),
        )
        self.vitrine = Equipamento.objects.create(nome='Vitrine refrigerada', unidade=self.centro)

    def equipamentos(self, **parametros):
        resposta = self.client.get(reverse('equipamentos_lista'), parametros)
        return list(resposta.context['equipamentos'])

    def test_rotas_seguem_o_padrao_documentado(self):
        self.assertEqual(reverse('equipamentos_lista'), '/manutencao/equipamentos/')
        self.assertEqual(reverse('equipamentos_criar'), '/manutencao/equipamentos/novo/')
        self.assertEqual(reverse('equipamentos_editar', args=[7]), '/manutencao/equipamentos/7/editar/')
        self.assertEqual(reverse('equipamentos_excluir', args=[7]), '/manutencao/equipamentos/7/excluir/')

    def test_lista_mostra_dados_do_equipamento(self):
        resposta = self.client.get(reverse('equipamentos_lista'))
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, 'Forno de lastro')
        self.assertContains(resposta, 'Lastro 6 esteiras')
        self.assertContains(resposta, '10/03/2021')

    def test_conta_manutencoes_em_aberto(self):
        for status in ['pendente', 'em_andamento', 'concluida']:
            Manutencao.objects.create(
                equipamento=self.forno, tipo='corretiva', descricao='Reparo',
                data=date(2026, 11, 1), status=status,
            )
        resposta = self.client.get(reverse('equipamentos_lista'))
        em_aberto = {e.nome: e.em_aberto for e in resposta.context['equipamentos']}
        self.assertEqual(em_aberto, {'Forno de lastro': 2, 'Vitrine refrigerada': 0})
        self.assertContains(resposta, '2 em aberto')
        self.assertContains(resposta, 'Em dia')

    def test_lista_em_ordem_alfabetica(self):
        Equipamento.objects.create(nome='Câmara fria', unidade=self.fabrica)
        nomes = [e.nome for e in self.equipamentos()]
        self.assertEqual(nomes, ['Câmara fria', 'Forno de lastro', 'Vitrine refrigerada'])

    def test_filtro_por_unidade(self):
        self.assertEqual(self.equipamentos(unidade=self.centro.pk), [self.vitrine])

    def test_busca_por_marca_e_modelo(self):
        self.assertEqual(self.equipamentos(q='esteiras'), [self.forno])

    def test_filtros_sem_resultado_mostram_aviso(self):
        resposta = self.client.get(reverse('equipamentos_lista'), {'q': 'geladeira'})
        self.assertContains(resposta, 'Nenhum equipamento encontrado com estes filtros.')

    def test_cadastro_cria_equipamento(self):
        resposta = self.client.post(reverse('equipamentos_criar'), {
            'nome': 'Masseira espiral', 'unidade': self.fabrica.pk,
            'marca_modelo': '', 'data_aquisicao': '', 'observacoes': '',
        }, follow=True)
        self.assertRedirects(resposta, reverse('equipamentos_lista'))
        self.assertTrue(Equipamento.objects.filter(nome='Masseira espiral').exists())
        self.assertContains(resposta, 'Equipamento cadastrado com sucesso.')

    def test_cadastro_sem_unidade_mostra_erro(self):
        resposta = self.client.post(reverse('equipamentos_criar'), {'nome': 'Masseira'})
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, 'Este campo é obrigatório.')
        self.assertEqual(Equipamento.objects.count(), 2)

    def test_edicao_abre_com_data_preenchida(self):
        resposta = self.client.get(reverse('equipamentos_editar', args=[self.forno.pk]))
        self.assertContains(resposta, 'value="2021-03-10"')

    def test_edicao_transfere_equipamento_de_unidade(self):
        resposta = self.client.post(reverse('equipamentos_editar', args=[self.vitrine.pk]), {
            'nome': 'Vitrine refrigerada', 'unidade': self.fabrica.pk,
        }, follow=True)
        self.assertRedirects(resposta, reverse('equipamentos_lista'))
        self.vitrine.refresh_from_db()
        self.assertEqual(self.vitrine.unidade, self.fabrica)

    def test_exclusao_remove_equipamento_e_historico(self):
        Manutencao.objects.create(
            equipamento=self.forno, tipo='preventiva', descricao='Limpeza', data=date(2026, 11, 1),
        )
        url = reverse('equipamentos_excluir', args=[self.forno.pk])
        resposta = self.client.get(url)
        self.assertContains(resposta, 'Forno de lastro (Fábrica)')
        resposta = self.client.post(url, follow=True)
        self.assertFalse(Equipamento.objects.filter(pk=self.forno.pk).exists())
        self.assertEqual(Manutencao.objects.count(), 0)
        self.assertContains(resposta, 'Equipamento removido com sucesso.')
