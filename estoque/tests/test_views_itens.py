from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from estoque.models import ItemEstoque, Movimentacao
from unidades.models import Unidade


class ItensSemLoginTests(TestCase):
    """Nenhuma página do módulo abre sem autenticação."""

    def test_paginas_redirecionam_para_o_login(self):
        unidade = Unidade.objects.create(nome='Fábrica', endereco='Distrito Industrial')
        item = ItemEstoque.objects.create(
            nome='Sal', tipo='insumo', unidade_medida='kg', unidade=unidade,
        )
        urls = [
            reverse('estoque_lista'),
            reverse('estoque_criar'),
            reverse('estoque_editar', args=[item.pk]),
            reverse('estoque_excluir', args=[item.pk]),
        ]
        for url in urls:
            with self.subTest(url=url):
                resposta = self.client.get(url)
                self.assertRedirects(resposta, f'/login/?next={url}')


class ItensViewsTests(TestCase):
    def setUp(self):
        usuario = get_user_model().objects.create_user(
            username='gerente',
            password='senha-de-teste-123',
        )
        self.client.force_login(usuario)
        self.fabrica = Unidade.objects.create(nome='Fábrica', endereco='Distrito Industrial')
        self.centro = Unidade.objects.create(nome='Unidade Centro', endereco='Rua A, 10')
        self.farinha = ItemEstoque.objects.create(
            nome='Farinha de trigo', tipo='insumo', unidade_medida='kg', unidade=self.fabrica,
            quantidade=Decimal('95.5'), quantidade_minima=Decimal('50'),
        )
        self.pao = ItemEstoque.objects.create(
            nome='Pão francês', tipo='produto', unidade_medida='un', unidade=self.centro,
            quantidade=Decimal('80'), quantidade_minima=Decimal('100'),
        )

    def dados(self, **alteracoes):
        dados = {
            'nome': 'Manteiga',
            'tipo': 'insumo',
            'unidade_medida': 'kg',
            'unidade': self.fabrica.pk,
            'fornecedor': '',
            'quantidade_minima': '10',
        }
        dados.update(alteracoes)
        return dados

    def itens(self, resposta):
        return list(resposta.context['itens'])

    def test_rotas_seguem_o_padrao_documentado(self):
        self.assertEqual(reverse('estoque_lista'), '/estoque/')
        self.assertEqual(reverse('estoque_criar'), '/estoque/novo/')
        self.assertEqual(reverse('estoque_editar', args=[7]), '/estoque/7/editar/')
        self.assertEqual(reverse('estoque_excluir', args=[7]), '/estoque/7/excluir/')

    def test_lista_mostra_quantidade_formatada_e_situacao(self):
        resposta = self.client.get(reverse('estoque_lista'))
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, '95,5 kg')
        self.assertContains(resposta, 'mínimo 50')
        self.assertContains(resposta, 'Estoque baixo')

    def test_lista_avisa_quantos_itens_estao_com_estoque_baixo(self):
        resposta = self.client.get(reverse('estoque_lista'))
        self.assertContains(resposta, '1 item com estoque baixo.')

    def test_filtro_so_estoque_baixo(self):
        resposta = self.client.get(reverse('estoque_lista'), {'baixo': '1'})
        self.assertEqual(self.itens(resposta), [self.pao])

    def test_filtros_por_unidade_e_tipo(self):
        resposta = self.client.get(reverse('estoque_lista'), {'unidade': self.fabrica.pk})
        self.assertEqual(self.itens(resposta), [self.farinha])
        resposta = self.client.get(reverse('estoque_lista'), {'tipo': 'produto'})
        self.assertEqual(self.itens(resposta), [self.pao])

    def test_busca_por_nome(self):
        resposta = self.client.get(reverse('estoque_lista'), {'q': 'farinha'})
        self.assertEqual(self.itens(resposta), [self.farinha])

    def test_filtros_sem_resultado_mostram_aviso(self):
        resposta = self.client.get(reverse('estoque_lista'), {'q': 'chocolate'})
        self.assertContains(resposta, 'Nenhum item encontrado com estes filtros.')

    def test_cadastro_cria_item_com_quantidade_zero(self):
        resposta = self.client.post(reverse('estoque_criar'), self.dados(), follow=True)
        self.assertRedirects(resposta, reverse('estoque_lista'))
        item = ItemEstoque.objects.get(nome='Manteiga')
        self.assertEqual(item.quantidade, Decimal('0'))
        self.assertContains(resposta, 'Item &quot;Manteiga&quot; cadastrado com sucesso.')

    def test_cadastro_ignora_quantidade_enviada_pelo_formulario(self):
        self.client.post(reverse('estoque_criar'), self.dados(quantidade='999'))
        self.assertEqual(ItemEstoque.objects.get(nome='Manteiga').quantidade, Decimal('0'))

    def test_cadastro_de_item_repetido_na_unidade_mostra_erro(self):
        resposta = self.client.post(
            reverse('estoque_criar'), self.dados(nome='Farinha de trigo'),
        )
        self.assertContains(resposta, 'Este item já está cadastrado nesta unidade.')

    def test_edicao_nao_altera_a_quantidade(self):
        resposta = self.client.post(
            reverse('estoque_editar', args=[self.farinha.pk]),
            self.dados(nome='Farinha de trigo tipo 1', quantidade_minima='40'),
            follow=True,
        )
        self.assertRedirects(resposta, reverse('estoque_lista'))
        self.farinha.refresh_from_db()
        self.assertEqual(self.farinha.nome, 'Farinha de trigo tipo 1')
        self.assertEqual(self.farinha.quantidade_minima, Decimal('40'))
        self.assertEqual(self.farinha.quantidade, Decimal('95.5'))

    def test_edicao_mostra_quantidade_atual(self):
        resposta = self.client.get(reverse('estoque_editar', args=[self.farinha.pk]))
        self.assertContains(resposta, 'Quantidade atual: 95,5 kg.')

    def test_exclusao_remove_item_e_historico(self):
        Movimentacao.objects.create(
            item=self.farinha, tipo='entrada', quantidade=Decimal('95.5'),
            saldo_apos=Decimal('95.5'),
        )
        url = reverse('estoque_excluir', args=[self.farinha.pk])
        resposta = self.client.get(url)
        self.assertTemplateUsed(resposta, 'cadastros/confirmar_exclusao.html')

        resposta = self.client.post(url, follow=True)
        self.assertRedirects(resposta, reverse('estoque_lista'))
        self.assertFalse(ItemEstoque.objects.filter(pk=self.farinha.pk).exists())
        self.assertEqual(Movimentacao.objects.count(), 0)
        self.assertContains(resposta, 'Item removido com sucesso.')
