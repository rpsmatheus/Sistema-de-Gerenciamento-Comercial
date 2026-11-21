from datetime import date, timedelta
from decimal import Decimal
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from faturamento.models import Lancamento
from unidades.models import Unidade


class FaturamentoSemLoginTests(TestCase):
    def test_paginas_redirecionam_para_o_login(self):
        unidade = Unidade.objects.create(nome='Unidade Centro', endereco='Rua A, 10')
        lancamento = Lancamento.objects.create(
            unidade=unidade, data=date(2026, 11, 8), valor=Decimal('10'), descricao='Teste',
        )
        urls = [
            reverse('faturamento_lista'),
            reverse('faturamento_criar'),
            reverse('faturamento_editar', args=[lancamento.pk]),
            reverse('faturamento_excluir', args=[lancamento.pk]),
        ]
        for url in urls:
            with self.subTest(url=url):
                resposta = self.client.get(url)
                self.assertRedirects(resposta, f'/login/?next={url}')


class FaturamentoViewsTests(TestCase):
    def setUp(self):
        usuario = get_user_model().objects.create_user(
            username='gerente',
            password='senha-de-teste-123',
        )
        self.client.force_login(usuario)
        self.centro = Unidade.objects.create(nome='Unidade Centro', endereco='Rua A, 10')
        self.jardim = Unidade.objects.create(nome='Unidade Jardim', endereco='Rua B, 20')
        self.outubro = Lancamento.objects.create(
            unidade=self.centro, data=date(2026, 10, 25),
            valor=Decimal('8450.00'), descricao='Vendas do balcão',
        )
        self.novembro = Lancamento.objects.create(
            unidade=self.centro, data=date(2026, 11, 8),
            valor=Decimal('1234.56'), descricao='Encomenda do hotel',
        )
        self.jardim_novembro = Lancamento.objects.create(
            unidade=self.jardim, data=date(2026, 11, 8),
            valor=Decimal('6320.00'), descricao='Vendas do balcão',
        )

    def lista(self, **parametros):
        return self.client.get(reverse('faturamento_lista'), parametros)

    def test_rotas_seguem_o_padrao_documentado(self):
        self.assertEqual(reverse('faturamento_lista'), '/faturamento/')
        self.assertEqual(reverse('faturamento_criar'), '/faturamento/novo/')
        self.assertEqual(reverse('faturamento_editar', args=[7]), '/faturamento/7/editar/')
        self.assertEqual(reverse('faturamento_excluir', args=[7]), '/faturamento/7/excluir/')

    def test_lista_mostra_valores_em_reais(self):
        resposta = self.lista()
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, 'R$ 1.234,56')
        self.assertContains(resposta, '25/10/2026')

    def test_total_geral_e_por_unidade(self):
        resposta = self.lista()
        self.assertEqual(resposta.context['total'], Decimal('16004.56'))
        self.assertContains(resposta, 'R$ 16.004,56')
        totais = {linha['unidade__nome']: linha['total'] for linha in resposta.context['totais_por_unidade']}
        self.assertEqual(totais, {
            'Unidade Centro': Decimal('9684.56'),
            'Unidade Jardim': Decimal('6320.00'),
        })

    def test_filtro_por_periodo_atualiza_o_total(self):
        resposta = self.lista(de='2026-11-01', ate='2026-11-30')
        self.assertEqual(
            list(resposta.context['lancamentos']), [self.jardim_novembro, self.novembro],
        )
        self.assertEqual(resposta.context['total'], Decimal('7554.56'))
        self.assertContains(resposta, 'Total filtrado')

    def test_filtro_por_unidade(self):
        resposta = self.lista(unidade=self.jardim.pk)
        self.assertEqual(list(resposta.context['lancamentos']), [self.jardim_novembro])
        self.assertEqual(resposta.context['total'], Decimal('6320.00'))

    def test_total_considera_todas_as_paginas(self):
        for dia in range(1, 26):
            Lancamento.objects.create(
                unidade=self.centro, data=date(2026, 9, dia),
                valor=Decimal('100'), descricao='Vendas',
            )
        resposta = self.lista(de='2026-09-01', ate='2026-09-30')
        self.assertEqual(len(resposta.context['lancamentos']), 20)
        self.assertEqual(resposta.context['quantidade'], 25)
        self.assertEqual(resposta.context['total'], Decimal('2500'))

    def test_busca_pela_descricao(self):
        resposta = self.lista(q='hotel')
        self.assertEqual(list(resposta.context['lancamentos']), [self.novembro])

    def test_datas_invalidas_sao_ignoradas(self):
        resposta = self.lista(de='ontem')
        self.assertEqual(resposta.context['quantidade'], 3)

    def test_filtros_sem_resultado_mostram_aviso(self):
        resposta = self.lista(de='2030-01-01')
        self.assertContains(resposta, 'Nenhum lançamento encontrado com estes filtros.')

    def test_atalhos_de_periodo(self):
        with mock.patch('django.utils.timezone.localdate', return_value=date(2026, 11, 16)):
            resposta = self.lista()
        self.assertContains(resposta, '?de=2026-11-01&amp;ate=2026-11-16')
        self.assertContains(resposta, '?de=2026-10-01&amp;ate=2026-10-31')

    def test_cadastro_cria_lancamento(self):
        ontem = (date.today() - timedelta(days=1)).isoformat()
        resposta = self.client.post(reverse('faturamento_criar'), {
            'unidade': self.jardim.pk, 'data': ontem,
            'valor': '960.00', 'descricao': 'Encomenda de bolos',
        }, follow=True)
        self.assertRedirects(resposta, reverse('faturamento_lista'))
        self.assertTrue(Lancamento.objects.filter(descricao='Encomenda de bolos').exists())
        self.assertContains(resposta, 'Lançamento cadastrado com sucesso.')

    def test_cadastro_com_valor_invalido_mostra_erro(self):
        resposta = self.client.post(reverse('faturamento_criar'), {
            'unidade': self.jardim.pk, 'data': '2026-11-01', 'valor': '0', 'descricao': 'X',
        })
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(Lancamento.objects.count(), 3)

    def test_edicao_altera_o_valor(self):
        resposta = self.client.post(reverse('faturamento_editar', args=[self.novembro.pk]), {
            'unidade': self.centro.pk, 'data': '2026-11-08',
            'valor': '1500.00', 'descricao': 'Encomenda do hotel',
        }, follow=True)
        self.assertRedirects(resposta, reverse('faturamento_lista'))
        self.novembro.refresh_from_db()
        self.assertEqual(self.novembro.valor, Decimal('1500.00'))

    def test_exclusao_pede_confirmacao_e_remove(self):
        url = reverse('faturamento_excluir', args=[self.novembro.pk])
        resposta = self.client.get(url)
        self.assertTemplateUsed(resposta, 'cadastros/confirmar_exclusao.html')
        resposta = self.client.post(url, follow=True)
        self.assertFalse(Lancamento.objects.filter(pk=self.novembro.pk).exists())
        self.assertContains(resposta, 'Lançamento removido com sucesso.')
