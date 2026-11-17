from datetime import datetime
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from estoque.models import ItemEstoque, Movimentacao
from estoque.services import registrar_movimentacao
from unidades.models import Unidade


class MovimentacoesSemLoginTests(TestCase):
    def test_paginas_redirecionam_para_o_login(self):
        unidade = Unidade.objects.create(nome='Fábrica', endereco='Distrito Industrial')
        item = ItemEstoque.objects.create(
            nome='Sal', tipo='insumo', unidade_medida='kg', unidade=unidade,
        )
        for url in [reverse('estoque_movimentar', args=[item.pk]), reverse('estoque_movimentacoes')]:
            with self.subTest(url=url):
                resposta = self.client.get(url)
                self.assertRedirects(resposta, f'/login/?next={url}')


class MovimentarViewTests(TestCase):
    def setUp(self):
        usuario = get_user_model().objects.create_user(
            username='gerente',
            password='senha-de-teste-123',
        )
        self.client.force_login(usuario)
        unidade = Unidade.objects.create(nome='Fábrica', endereco='Distrito Industrial')
        self.item = ItemEstoque.objects.create(
            nome='Farinha de trigo', tipo='insumo', unidade_medida='kg', unidade=unidade,
            quantidade_minima=Decimal('50'),
        )
        registrar_movimentacao(self.item, 'entrada', Decimal('95'), 'Estoque inicial')
        self.url = reverse('estoque_movimentar', args=[self.item.pk])

    def test_rotas_seguem_o_padrao_documentado(self):
        self.assertEqual(reverse('estoque_movimentar', args=[7]), '/estoque/7/movimentar/')
        self.assertEqual(reverse('estoque_movimentacoes'), '/estoque/movimentacoes/')

    def test_pagina_mostra_o_saldo_atual(self):
        resposta = self.client.get(self.url)
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, 'Farinha de trigo')
        self.assertContains(resposta, 'Saldo atual: <strong>95 kg</strong>', html=False)
        self.assertContains(resposta, 'Em quilograma (kg).')

    def test_item_inexistente_retorna_404(self):
        resposta = self.client.get(reverse('estoque_movimentar', args=[9999]))
        self.assertEqual(resposta.status_code, 404)

    def test_entrada_aumenta_o_saldo_e_mostra_mensagem(self):
        resposta = self.client.post(self.url, {
            'tipo': 'entrada', 'quantidade': '50', 'observacao': 'Compra do moinho',
        }, follow=True)
        self.assertRedirects(resposta, reverse('estoque_lista'))
        self.item.refresh_from_db()
        self.assertEqual(self.item.quantidade, Decimal('145'))
        self.assertContains(
            resposta, 'Entrada de 50 kg registrada para Farinha de trigo. Saldo atual: 145 kg.',
        )

    def test_saida_diminui_o_saldo(self):
        resposta = self.client.post(self.url, {
            'tipo': 'saida', 'quantidade': '12.5', 'observacao': '',
        }, follow=True)
        self.item.refresh_from_db()
        self.assertEqual(self.item.quantidade, Decimal('82.5'))
        self.assertContains(resposta, 'Saída de 12,5 kg registrada')

    def test_saida_maior_que_o_saldo_e_bloqueada(self):
        resposta = self.client.post(self.url, {'tipo': 'saida', 'quantidade': '100'})
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, 'Estoque insuficiente: há apenas 95 kg disponíveis.')
        self.item.refresh_from_db()
        self.assertEqual(self.item.quantidade, Decimal('95'))
        self.assertEqual(Movimentacao.objects.count(), 1)

    def test_quantidade_zero_mostra_erro(self):
        resposta = self.client.post(self.url, {'tipo': 'entrada', 'quantidade': '0'})
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(Movimentacao.objects.count(), 1)

    def test_lista_do_estoque_tem_links_de_movimentar_e_historico(self):
        resposta = self.client.get(reverse('estoque_lista'))
        self.assertContains(resposta, f'href="{self.url}"')
        self.assertContains(resposta, f'href="/estoque/movimentacoes/?item={self.item.pk}"')
        self.assertContains(resposta, 'Histórico de movimentações')


class HistoricoViewTests(TestCase):
    def setUp(self):
        usuario = get_user_model().objects.create_user(
            username='gerente',
            password='senha-de-teste-123',
        )
        self.client.force_login(usuario)
        unidade = Unidade.objects.create(nome='Fábrica', endereco='Distrito Industrial')
        self.farinha = ItemEstoque.objects.create(
            nome='Farinha de trigo', tipo='insumo', unidade_medida='kg', unidade=unidade,
        )
        self.ovos = ItemEstoque.objects.create(
            nome='Ovos', tipo='insumo', unidade_medida='un', unidade=unidade,
        )
        self.entrada = registrar_movimentacao(self.farinha, 'entrada', Decimal('100'), 'Compra')
        self.saida = registrar_movimentacao(self.farinha, 'saida', Decimal('30'), 'Produção')
        self.ovos_entrada = registrar_movimentacao(self.ovos, 'entrada', Decimal('360'))
        # Datas fixas, para os filtros por período.
        fuso = timezone.get_current_timezone()
        for movimentacao, dia in [(self.entrada, 3), (self.saida, 5), (self.ovos_entrada, 10)]:
            movimentacao.data = datetime(2026, 11, dia, 10, 0, tzinfo=fuso)
            movimentacao.save(update_fields=['data'])

    def movimentacoes(self, **parametros):
        resposta = self.client.get(reverse('estoque_movimentacoes'), parametros)
        return list(resposta.context['movimentacoes'])

    def test_historico_mostra_mais_recentes_primeiro(self):
        self.assertEqual(self.movimentacoes(), [self.ovos_entrada, self.saida, self.entrada])

    def test_historico_mostra_sinal_e_saldo(self):
        resposta = self.client.get(reverse('estoque_movimentacoes'))
        self.assertContains(resposta, '+100 kg')
        self.assertContains(resposta, '−30 kg')
        self.assertContains(resposta, '70 kg')
        self.assertContains(resposta, '05/11/2026 10:00')

    def test_filtro_por_item(self):
        self.assertEqual(self.movimentacoes(item=self.ovos.pk), [self.ovos_entrada])

    def test_filtro_por_tipo(self):
        self.assertEqual(self.movimentacoes(tipo='saida'), [self.saida])

    def test_filtro_por_periodo(self):
        self.assertEqual(self.movimentacoes(de='2026-11-04', ate='2026-11-09'), [self.saida])
        self.assertEqual(self.movimentacoes(de='2026-11-05'), [self.ovos_entrada, self.saida])

    def test_datas_invalidas_sao_ignoradas(self):
        self.assertEqual(len(self.movimentacoes(de='ontem', ate='31/02')), 3)

    def test_busca_por_observacao(self):
        self.assertEqual(self.movimentacoes(q='produção'), [self.saida])

    def test_filtros_sem_resultado_mostram_aviso(self):
        resposta = self.client.get(reverse('estoque_movimentacoes'), {'de': '2030-01-01'})
        self.assertContains(resposta, 'Nenhuma movimentação encontrada com estes filtros.')
