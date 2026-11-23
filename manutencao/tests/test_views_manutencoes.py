from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from fornecedores.models import Fornecedor
from manutencao.models import Equipamento, Manutencao
from unidades.models import Unidade


class ManutencoesSemLoginTests(TestCase):
    def test_paginas_redirecionam_para_o_login(self):
        unidade = Unidade.objects.create(nome='Fábrica', endereco='Distrito Industrial')
        forno = Equipamento.objects.create(nome='Forno', unidade=unidade)
        manutencao = Manutencao.objects.create(
            equipamento=forno, tipo='preventiva', descricao='Limpeza', data=date(2026, 11, 1),
        )
        urls = [
            reverse('manutencao_lista'),
            reverse('manutencao_criar'),
            reverse('manutencao_editar', args=[manutencao.pk]),
            reverse('manutencao_excluir', args=[manutencao.pk]),
        ]
        for url in urls:
            with self.subTest(url=url):
                resposta = self.client.get(url)
                self.assertRedirects(resposta, f'/login/?next={url}')


class ManutencoesViewsTests(TestCase):
    def setUp(self):
        usuario = get_user_model().objects.create_user(
            username='gerente',
            password='senha-de-teste-123',
        )
        self.client.force_login(usuario)
        self.fabrica = Unidade.objects.create(nome='Fábrica', endereco='Distrito Industrial')
        self.centro = Unidade.objects.create(nome='Unidade Centro', endereco='Rua A, 10')
        self.tecforno = Fornecedor.objects.create(razao_social='TecForno Ltda', nome_fantasia='TecForno', cnpj='66777888000199')
        self.forno = Equipamento.objects.create(nome='Forno de lastro', unidade=self.fabrica)
        self.vitrine = Equipamento.objects.create(nome='Vitrine refrigerada', unidade=self.centro)
        self.revisao = Manutencao.objects.create(
            equipamento=self.forno, tipo='preventiva', descricao='Revisão trimestral',
            data=date(2026, 9, 15), custo=Decimal('350.00'), status='concluida',
            fornecedor=self.tecforno,
        )
        self.termostato = Manutencao.objects.create(
            equipamento=self.forno, tipo='corretiva', descricao='Troca do termostato',
            data=date(2026, 11, 3), custo=Decimal('480.00'), status='em_andamento',
        )
        self.filtro = Manutencao.objects.create(
            equipamento=self.vitrine, tipo='preventiva', descricao='Troca do filtro',
            data=date(2026, 11, 10), status='pendente',
        )

    def manutencoes(self, **parametros):
        resposta = self.client.get(reverse('manutencao_lista'), parametros)
        return list(resposta.context['manutencoes'])

    def test_rotas_seguem_o_padrao_documentado(self):
        self.assertEqual(reverse('manutencao_lista'), '/manutencao/')
        self.assertEqual(reverse('manutencao_criar'), '/manutencao/nova/')
        self.assertEqual(reverse('manutencao_editar', args=[7]), '/manutencao/7/editar/')
        self.assertEqual(reverse('manutencao_excluir', args=[7]), '/manutencao/7/excluir/')

    def test_lista_mostra_status_custo_e_prestador(self):
        resposta = self.client.get(reverse('manutencao_lista'))
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, 'Revisão trimestral')
        self.assertContains(resposta, 'Preventiva · TecForno')
        self.assertContains(resposta, 'R$ 350,00')
        self.assertContains(resposta, 'etiqueta-andamento')
        self.assertContains(resposta, 'etiqueta-pendente')

    def test_mais_recentes_primeiro(self):
        self.assertEqual(self.manutencoes(), [self.filtro, self.termostato, self.revisao])

    def test_custo_total_e_contagem_por_status(self):
        resposta = self.client.get(reverse('manutencao_lista'))
        self.assertEqual(resposta.context['custo_total'], Decimal('830.00'))
        self.assertContains(resposta, 'R$ 830,00')
        contagem = {valor: total for valor, rotulo, total in resposta.context['por_status']}
        self.assertEqual(contagem, {'pendente': 1, 'em_andamento': 1, 'concluida': 1})

    def test_filtro_em_aberto_junta_pendentes_e_em_andamento(self):
        self.assertEqual(self.manutencoes(status='aberta'), [self.filtro, self.termostato])

    def test_filtros_por_equipamento_unidade_e_tipo(self):
        self.assertEqual(self.manutencoes(equipamento=self.vitrine.pk), [self.filtro])
        self.assertEqual(self.manutencoes(unidade=self.fabrica.pk), [self.termostato, self.revisao])
        self.assertEqual(self.manutencoes(tipo='corretiva'), [self.termostato])

    def test_filtro_por_periodo(self):
        self.assertEqual(self.manutencoes(de='2026-11-01', ate='2026-11-05'), [self.termostato])

    def test_busca_por_nome_do_equipamento(self):
        self.assertEqual(self.manutencoes(q='vitrine'), [self.filtro])

    def test_filtros_sem_resultado_mostram_aviso(self):
        resposta = self.client.get(reverse('manutencao_lista'), {'q': 'compressor'})
        self.assertContains(resposta, 'Nenhuma manutenção encontrada com estes filtros.')

    def test_nova_manutencao_ja_vem_com_o_equipamento_da_url(self):
        resposta = self.client.get(reverse('manutencao_criar'), {'equipamento': self.vitrine.pk})
        self.assertEqual(resposta.context['form'].initial['equipamento'], str(self.vitrine.pk))
        self.assertContains(resposta, f'<option value="{self.vitrine.pk}" selected>')

    def test_registro_cria_manutencao(self):
        resposta = self.client.post(reverse('manutencao_criar'), {
            'equipamento': self.forno.pk, 'tipo': 'corretiva', 'data': '2026-11-12',
            'descricao': 'Troca da lâmpada', 'status': 'pendente', 'custo': '0', 'fornecedor': '',
        }, follow=True)
        self.assertRedirects(resposta, reverse('manutencao_lista'))
        self.assertTrue(Manutencao.objects.filter(descricao='Troca da lâmpada').exists())
        self.assertContains(resposta, 'Manutenção registrada com sucesso.')

    def test_concluida_no_futuro_mostra_erro(self):
        futuro = (date.today() + timedelta(days=5)).isoformat()
        resposta = self.client.post(reverse('manutencao_criar'), {
            'equipamento': self.forno.pk, 'tipo': 'preventiva', 'data': futuro,
            'descricao': 'Revisão', 'status': 'concluida', 'custo': '0',
        })
        self.assertContains(resposta, 'Uma manutenção concluída não pode ter data no futuro.')
        self.assertEqual(Manutencao.objects.count(), 3)

    def test_edicao_conclui_a_manutencao(self):
        resposta = self.client.post(reverse('manutencao_editar', args=[self.termostato.pk]), {
            'equipamento': self.forno.pk, 'tipo': 'corretiva', 'data': '2026-11-03',
            'descricao': 'Troca do termostato', 'status': 'concluida',
            'custo': '480.00', 'fornecedor': self.tecforno.pk,
        }, follow=True)
        self.assertRedirects(resposta, reverse('manutencao_lista'))
        self.termostato.refresh_from_db()
        self.assertEqual(self.termostato.status, 'concluida')
        self.assertEqual(self.termostato.fornecedor, self.tecforno)

    def test_exclusao_pede_confirmacao_e_remove(self):
        url = reverse('manutencao_excluir', args=[self.filtro.pk])
        resposta = self.client.get(url)
        self.assertTemplateUsed(resposta, 'cadastros/confirmar_exclusao.html')
        resposta = self.client.post(url, follow=True)
        self.assertFalse(Manutencao.objects.filter(pk=self.filtro.pk).exists())
        self.assertContains(resposta, 'Manutenção removida com sucesso.')

    def test_lista_de_equipamentos_tem_links_para_manutencoes(self):
        resposta = self.client.get(reverse('equipamentos_lista'))
        self.assertContains(resposta, f'/manutencao/nova/?equipamento={self.forno.pk}')
        self.assertContains(resposta, f'/manutencao/?equipamento={self.forno.pk}&amp;status=aberta')
        self.assertContains(resposta, 'Ver manutenções')
