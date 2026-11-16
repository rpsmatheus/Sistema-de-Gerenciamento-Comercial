from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from estoque.models import ItemEstoque, Movimentacao
from estoque.services import registrar_movimentacao
from unidades.models import Unidade


class RegistrarMovimentacaoTests(TestCase):
    def setUp(self):
        unidade = Unidade.objects.create(nome='Fábrica', endereco='Distrito Industrial')
        self.item = ItemEstoque.objects.create(
            nome='Farinha de trigo', tipo='insumo', unidade_medida='kg', unidade=unidade,
        )

    def test_entrada_aumenta_o_saldo_e_registra_historico(self):
        movimentacao = registrar_movimentacao(self.item, 'entrada', Decimal('50'), 'Compra')
        self.item.refresh_from_db()
        self.assertEqual(self.item.quantidade, Decimal('50'))
        self.assertEqual(movimentacao.saldo_apos, Decimal('50'))
        self.assertEqual(movimentacao.observacao, 'Compra')

    def test_saida_diminui_o_saldo(self):
        registrar_movimentacao(self.item, 'entrada', Decimal('50'))
        movimentacao = registrar_movimentacao(self.item, 'saida', Decimal('12.5'))
        self.item.refresh_from_db()
        self.assertEqual(self.item.quantidade, Decimal('37.5'))
        self.assertEqual(movimentacao.saldo_apos, Decimal('37.5'))

    def test_saida_de_todo_o_saldo_e_permitida(self):
        registrar_movimentacao(self.item, 'entrada', Decimal('10'))
        registrar_movimentacao(self.item, 'saida', Decimal('10'))
        self.item.refresh_from_db()
        self.assertEqual(self.item.quantidade, Decimal('0'))

    def test_saida_maior_que_o_saldo_e_bloqueada_sem_alterar_nada(self):
        registrar_movimentacao(self.item, 'entrada', Decimal('10'))
        with self.assertRaisesMessage(ValidationError, 'Estoque insuficiente: há apenas 10 kg'):
            registrar_movimentacao(self.item, 'saida', Decimal('10.001'))
        self.item.refresh_from_db()
        self.assertEqual(self.item.quantidade, Decimal('10'))
        self.assertEqual(Movimentacao.objects.count(), 1)

    def test_quantidade_zero_ou_negativa_e_recusada(self):
        for quantidade in [Decimal('0'), Decimal('-5')]:
            with self.subTest(quantidade=quantidade):
                with self.assertRaisesMessage(ValidationError, 'maior que zero'):
                    registrar_movimentacao(self.item, 'entrada', quantidade)
        self.assertEqual(Movimentacao.objects.count(), 0)

    def test_tipo_invalido_e_recusado(self):
        with self.assertRaises(ValidationError):
            registrar_movimentacao(self.item, 'emprestimo', Decimal('5'))

    def test_usa_o_saldo_do_banco_e_nao_o_do_objeto(self):
        # Simula outra pessoa registrando uma saída enquanto este objeto
        # ainda guarda o saldo antigo.
        registrar_movimentacao(self.item, 'entrada', Decimal('10'))
        copia_desatualizada = ItemEstoque.objects.get(pk=self.item.pk)
        registrar_movimentacao(self.item, 'saida', Decimal('8'))
        with self.assertRaises(ValidationError):
            registrar_movimentacao(copia_desatualizada, 'saida', Decimal('5'))
