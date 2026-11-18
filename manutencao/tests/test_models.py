from datetime import date, timedelta
from decimal import Decimal

from django.db.models import ProtectedError
from django.test import TestCase

from fornecedores.models import Fornecedor
from manutencao.forms import EquipamentoForm, ManutencaoForm
from manutencao.models import Equipamento, Manutencao
from unidades.models import Unidade


class EquipamentoModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fabrica = Unidade.objects.create(nome='Fábrica', endereco='Distrito Industrial')

    def test_texto_mostra_nome_e_unidade(self):
        forno = Equipamento.objects.create(nome='Forno de lastro', unidade=self.fabrica)
        self.assertEqual(str(forno), 'Forno de lastro (Fábrica)')

    def test_unidade_com_equipamentos_nao_pode_ser_removida(self):
        Equipamento.objects.create(nome='Forno de lastro', unidade=self.fabrica)
        with self.assertRaises(ProtectedError):
            self.fabrica.delete()

    def test_remover_equipamento_remove_o_historico(self):
        forno = Equipamento.objects.create(nome='Forno de lastro', unidade=self.fabrica)
        Manutencao.objects.create(
            equipamento=forno, tipo='preventiva', descricao='Limpeza', data=date(2026, 11, 1),
        )
        forno.delete()
        self.assertEqual(Manutencao.objects.count(), 0)


class ManutencaoModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        fabrica = Unidade.objects.create(nome='Fábrica', endereco='Distrito Industrial')
        cls.forno = Equipamento.objects.create(nome='Forno de lastro', unidade=fabrica)

    def criar(self, **dados):
        valores = {
            'equipamento': self.forno,
            'tipo': Manutencao.Tipo.CORRETIVA,
            'descricao': 'Troca da resistência',
            'data': date(2026, 11, 3),
        }
        valores.update(dados)
        return Manutencao.objects.create(**valores)

    def test_texto_mostra_tipo_equipamento_e_data(self):
        self.assertEqual(str(self.criar()), 'Corretiva — Forno de lastro (03/11/2026)')

    def test_valores_padrao(self):
        manutencao = self.criar()
        self.assertEqual(manutencao.status, 'pendente')
        self.assertEqual(manutencao.custo, Decimal('0'))
        self.assertTrue(manutencao.aberta)

    def test_concluida_nao_esta_aberta(self):
        self.assertFalse(self.criar(status='concluida').aberta)

    def test_mais_recentes_primeiro(self):
        antiga = self.criar(data=date(2026, 10, 1))
        recente = self.criar(data=date(2026, 11, 1))
        self.assertEqual(list(Manutencao.objects.all()), [recente, antiga])

    def test_remover_fornecedor_mantem_a_manutencao(self):
        tecforno = Fornecedor.objects.create(razao_social='TecForno', cnpj='66777888000199')
        manutencao = self.criar(fornecedor=tecforno)
        tecforno.delete()
        manutencao.refresh_from_db()
        self.assertIsNone(manutencao.fornecedor)


class EquipamentoFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fabrica = Unidade.objects.create(nome='Fábrica', endereco='Distrito Industrial')

    def test_somente_nome_e_unidade_sao_obrigatorios(self):
        form = EquipamentoForm(data={'nome': 'Masseira', 'unidade': self.fabrica.pk})
        self.assertTrue(form.is_valid(), form.errors)

    def test_data_de_aquisicao_no_futuro_e_recusada(self):
        futuro = (date.today() + timedelta(days=2)).isoformat()
        form = EquipamentoForm(data={
            'nome': 'Masseira', 'unidade': self.fabrica.pk, 'data_aquisicao': futuro,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('A data de aquisição não pode estar no futuro.', form.errors['data_aquisicao'])


class ManutencaoFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        fabrica = Unidade.objects.create(nome='Fábrica', endereco='Distrito Industrial')
        cls.forno = Equipamento.objects.create(nome='Forno de lastro', unidade=fabrica)

    def dados(self, **alteracoes):
        dados = {
            'equipamento': self.forno.pk,
            'tipo': 'preventiva',
            'data': '2026-11-03',
            'descricao': 'Limpeza dos queimadores',
            'status': 'concluida',
            'custo': '350.00',
            'fornecedor': '',
        }
        dados.update(alteracoes)
        return dados

    def test_formulario_valido(self):
        form = ManutencaoForm(data=self.dados())
        self.assertTrue(form.is_valid(), form.errors)

    def test_pendente_pode_ser_agendada_para_o_futuro(self):
        futuro = (date.today() + timedelta(days=10)).isoformat()
        form = ManutencaoForm(data=self.dados(data=futuro, status='pendente', custo='0'))
        self.assertTrue(form.is_valid(), form.errors)

    def test_concluida_no_futuro_e_recusada(self):
        futuro = (date.today() + timedelta(days=10)).isoformat()
        form = ManutencaoForm(data=self.dados(data=futuro))
        self.assertFalse(form.is_valid())
        self.assertIn('Uma manutenção concluída não pode ter data no futuro.', form.errors['data'])

    def test_custo_negativo_e_recusado(self):
        form = ManutencaoForm(data=self.dados(custo='-10'))
        self.assertFalse(form.is_valid())
        self.assertIn('custo', form.errors)

    def test_equipamento_tipo_e_descricao_sao_obrigatorios(self):
        form = ManutencaoForm(data=self.dados(equipamento='', tipo='', descricao=''))
        self.assertFalse(form.is_valid())
        for campo in ['equipamento', 'tipo', 'descricao']:
            self.assertIn(campo, form.errors)
