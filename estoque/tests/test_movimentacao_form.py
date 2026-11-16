from decimal import Decimal

from django.test import TestCase

from estoque.forms import MovimentacaoForm
from estoque.models import ItemEstoque
from unidades.models import Unidade


class MovimentacaoFormTests(TestCase):
    def setUp(self):
        unidade = Unidade.objects.create(nome='Fábrica', endereco='Distrito Industrial')
        self.item = ItemEstoque.objects.create(
            nome='Ovos', tipo='insumo', unidade_medida='un', unidade=unidade,
            quantidade=Decimal('30'),
        )

    def form(self, **dados):
        valores = {'tipo': 'saida', 'quantidade': '10', 'observacao': ''}
        valores.update(dados)
        return MovimentacaoForm(data=valores, item=self.item)

    def test_saida_dentro_do_saldo_e_valida(self):
        self.assertTrue(self.form().is_valid())

    def test_saida_maior_que_o_saldo_mostra_erro_no_campo_quantidade(self):
        form = self.form(quantidade='31')
        self.assertFalse(form.is_valid())
        self.assertIn('Estoque insuficiente: há apenas 30 un disponíveis.', form.errors['quantidade'])

    def test_entrada_de_qualquer_valor_positivo_e_valida(self):
        self.assertTrue(self.form(tipo='entrada', quantidade='1000').is_valid())

    def test_quantidade_zero_e_recusada(self):
        form = self.form(tipo='entrada', quantidade='0')
        self.assertFalse(form.is_valid())
        self.assertIn('quantidade', form.errors)

    def test_tipo_e_obrigatorio(self):
        form = self.form(tipo='')
        self.assertFalse(form.is_valid())
        self.assertIn('tipo', form.errors)

    def test_ajuda_mostra_a_unidade_de_medida(self):
        self.assertEqual(self.form().fields['quantidade'].help_text, 'Em unidade (un).')
