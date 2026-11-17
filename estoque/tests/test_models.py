from decimal import Decimal

from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.test import TestCase

from estoque.forms import ItemEstoqueForm
from estoque.models import ItemEstoque, Movimentacao
from fornecedores.models import Fornecedor
from unidades.models import Unidade


class ItemEstoqueModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.centro = Unidade.objects.create(nome='Unidade Centro', endereco='Rua A, 10')
        cls.moinho = Fornecedor.objects.create(razao_social='Moinho', cnpj='11222333000144')

    def criar(self, **dados):
        valores = {
            'nome': 'Farinha de trigo',
            'tipo': ItemEstoque.Tipo.INSUMO,
            'unidade_medida': ItemEstoque.UnidadeMedida.KG,
            'unidade': self.centro,
            'quantidade_minima': Decimal('20'),
        }
        valores.update(dados)
        return ItemEstoque.objects.create(**valores)

    def test_texto_mostra_nome_e_unidade(self):
        self.assertEqual(str(self.criar()), 'Farinha de trigo (Unidade Centro)')

    def test_item_novo_comeca_com_quantidade_zero(self):
        self.assertEqual(self.criar().quantidade, Decimal('0'))

    def test_estoque_baixo_quando_quantidade_chega_ao_minimo(self):
        item = self.criar(quantidade=Decimal('20'))
        self.assertTrue(item.estoque_baixo)
        item.quantidade = Decimal('20.5')
        self.assertFalse(item.estoque_baixo)

    def test_mesmo_item_nao_pode_repetir_na_mesma_unidade(self):
        self.criar()
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.criar()

    def test_mesmo_item_pode_existir_em_outra_unidade(self):
        self.criar()
        jardim = Unidade.objects.create(nome='Unidade Jardim', endereco='Rua B, 20')
        self.criar(unidade=jardim)
        self.assertEqual(ItemEstoque.objects.count(), 2)

    def test_banco_recusa_quantidade_negativa(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.criar(quantidade=Decimal('-1'))

    def test_unidade_com_itens_nao_pode_ser_removida(self):
        self.criar()
        with self.assertRaises(ProtectedError):
            self.centro.delete()

    def test_remover_fornecedor_mantem_o_item_sem_fornecedor(self):
        item = self.criar(fornecedor=self.moinho)
        self.moinho.delete()
        item.refresh_from_db()
        self.assertIsNone(item.fornecedor)

    def test_remover_item_remove_o_historico(self):
        item = self.criar()
        Movimentacao.objects.create(
            item=item, tipo='entrada', quantidade=Decimal('5'), saldo_apos=Decimal('5'),
        )
        item.delete()
        self.assertEqual(Movimentacao.objects.count(), 0)


class MovimentacaoModelTests(TestCase):
    def test_movimentacoes_mais_recentes_primeiro(self):
        unidade = Unidade.objects.create(nome='Unidade Centro', endereco='Rua A, 10')
        item = ItemEstoque.objects.create(
            nome='Ovos', tipo='insumo', unidade_medida='un', unidade=unidade,
        )
        primeira = Movimentacao.objects.create(
            item=item, tipo='entrada', quantidade=Decimal('30'), saldo_apos=Decimal('30'),
        )
        segunda = Movimentacao.objects.create(
            item=item, tipo='saida', quantidade=Decimal('6'), saldo_apos=Decimal('24'),
        )
        self.assertEqual(list(Movimentacao.objects.all()), [segunda, primeira])
        self.assertTrue(primeira.eh_entrada)
        self.assertFalse(segunda.eh_entrada)
        self.assertEqual(segunda.get_tipo_display(), 'Saída')


class ItemEstoqueFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.centro = Unidade.objects.create(nome='Unidade Centro', endereco='Rua A, 10')

    def dados(self, **alteracoes):
        dados = {
            'nome': 'Farinha de trigo',
            'tipo': 'insumo',
            'unidade_medida': 'kg',
            'unidade': self.centro.pk,
            'fornecedor': '',
            'quantidade_minima': '20',
        }
        dados.update(alteracoes)
        return dados

    def test_formulario_valido_sem_fornecedor(self):
        form = ItemEstoqueForm(data=self.dados())
        self.assertTrue(form.is_valid(), form.errors)

    def test_formulario_nao_tem_campo_de_quantidade(self):
        self.assertNotIn('quantidade', ItemEstoqueForm().fields)

    def test_item_repetido_na_unidade_mostra_mensagem(self):
        ItemEstoque.objects.create(
            nome='Farinha de trigo', tipo='insumo', unidade_medida='kg', unidade=self.centro,
        )
        form = ItemEstoqueForm(data=self.dados())
        self.assertFalse(form.is_valid())
        self.assertIn('Este item já está cadastrado nesta unidade.', form.non_field_errors())

    def test_quantidade_minima_negativa_e_recusada(self):
        form = ItemEstoqueForm(data=self.dados(quantidade_minima='-1'))
        self.assertFalse(form.is_valid())
        self.assertIn('quantidade_minima', form.errors)

    def test_tipo_unidade_e_medida_sao_obrigatorios(self):
        form = ItemEstoqueForm(data=self.dados(tipo='', unidade='', unidade_medida=''))
        self.assertFalse(form.is_valid())
        for campo in ['tipo', 'unidade', 'unidade_medida']:
            self.assertIn(campo, form.errors)
