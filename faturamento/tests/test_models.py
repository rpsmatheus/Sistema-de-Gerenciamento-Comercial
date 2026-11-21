from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db.models import ProtectedError
from django.test import TestCase
from django.urls import reverse

from faturamento.forms import LancamentoForm
from faturamento.models import Lancamento
from unidades.models import Unidade


class LancamentoModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.centro = Unidade.objects.create(nome='Unidade Centro', endereco='Rua A, 10')

    def criar(self, **dados):
        valores = {
            'unidade': self.centro,
            'data': date(2026, 11, 8),
            'valor': Decimal('8450.00'),
            'descricao': 'Vendas do balcão',
        }
        valores.update(dados)
        return Lancamento.objects.create(**valores)

    def test_texto_mostra_descricao_unidade_e_data(self):
        self.assertEqual(str(self.criar()), 'Vendas do balcão — Unidade Centro (08/11/2026)')

    def test_mais_recentes_primeiro(self):
        antigo = self.criar(data=date(2026, 10, 1))
        recente = self.criar(data=date(2026, 11, 1))
        self.assertEqual(list(Lancamento.objects.all()), [recente, antigo])

    def test_unidade_com_lancamentos_nao_pode_ser_removida(self):
        self.criar()
        with self.assertRaises(ProtectedError):
            self.centro.delete()

    def test_aviso_de_exclusao_da_unidade_cita_lancamentos(self):
        self.criar()
        usuario = get_user_model().objects.create_user(username='gerente', password='x-123456')
        self.client.force_login(usuario)
        resposta = self.client.post(
            reverse('unidades_excluir', args=[self.centro.pk]), follow=True,
        )
        self.assertContains(resposta, 'porque tem lançamentos de faturamento vinculados')


class LancamentoFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.centro = Unidade.objects.create(nome='Unidade Centro', endereco='Rua A, 10')

    def dados(self, **alteracoes):
        dados = {
            'unidade': self.centro.pk,
            'data': '2026-11-08',
            'valor': '8450.00',
            'descricao': 'Vendas do balcão',
        }
        dados.update(alteracoes)
        return dados

    def test_formulario_valido(self):
        form = LancamentoForm(data=self.dados())
        self.assertTrue(form.is_valid(), form.errors)

    def test_data_de_hoje_vem_preenchida(self):
        self.assertEqual(LancamentoForm().initial['data'], date.today())

    def test_data_futura_e_recusada(self):
        amanha = (date.today() + timedelta(days=2)).isoformat()
        form = LancamentoForm(data=self.dados(data=amanha))
        self.assertFalse(form.is_valid())
        self.assertIn('Não é possível lançar faturamento em uma data futura.', form.errors['data'])

    def test_valor_zero_ou_negativo_e_recusado(self):
        for valor in ['0', '-10']:
            with self.subTest(valor=valor):
                form = LancamentoForm(data=self.dados(valor=valor))
                self.assertFalse(form.is_valid())
                self.assertIn('valor', form.errors)

    def test_valor_com_mais_de_duas_casas_e_recusado(self):
        form = LancamentoForm(data=self.dados(valor='10.555'))
        self.assertFalse(form.is_valid())
        self.assertIn('valor', form.errors)

    def test_unidade_e_descricao_sao_obrigatorias(self):
        form = LancamentoForm(data=self.dados(unidade='', descricao=''))
        self.assertFalse(form.is_valid())
        self.assertIn('unidade', form.errors)
        self.assertIn('descricao', form.errors)
