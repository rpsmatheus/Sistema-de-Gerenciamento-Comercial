from datetime import date, timedelta

from django.db.models import ProtectedError
from django.test import TestCase

from funcionarios.forms import FuncionarioForm
from funcionarios.models import Funcionario
from unidades.models import Unidade


class FuncionarioModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.unidade = Unidade.objects.create(nome='Unidade Centro', endereco='Rua A, 10')

    def criar(self, **dados):
        valores = {
            'nome': 'João Silva',
            'unidade': self.unidade,
            'cargo': Funcionario.Cargo.PADEIRO,
            'data_admissao': date(2025, 3, 1),
        }
        valores.update(dados)
        return Funcionario.objects.create(**valores)

    def test_texto_do_funcionario_e_o_nome(self):
        self.assertEqual(str(self.criar()), 'João Silva')

    def test_situacao_padrao_e_ativo(self):
        funcionario = self.criar()
        self.assertEqual(funcionario.situacao, 'ativo')
        self.assertTrue(funcionario.ativo)

    def test_cargo_tem_nome_para_exibir(self):
        funcionario = self.criar(cargo=Funcionario.Cargo.AUXILIAR)
        self.assertEqual(funcionario.get_cargo_display(), 'Auxiliar de produção')

    def test_unidade_lista_seus_funcionarios(self):
        self.criar(nome='João Silva')
        self.criar(nome='Ana Souza')
        nomes = list(self.unidade.funcionarios.values_list('nome', flat=True))
        self.assertEqual(nomes, ['Ana Souza', 'João Silva'])

    def test_unidade_com_funcionarios_nao_pode_ser_removida(self):
        self.criar()
        with self.assertRaises(ProtectedError):
            self.unidade.delete()


class FuncionarioFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.unidade = Unidade.objects.create(nome='Unidade Centro', endereco='Rua A, 10')

    def dados(self, **alteracoes):
        dados = {
            'nome': 'João Silva',
            'unidade': self.unidade.pk,
            'cargo': 'padeiro',
            'telefone': '(31) 99999-3001',
            'email': 'joao@exemplo.com',
            'data_admissao': '2025-03-01',
            'situacao': 'ativo',
        }
        dados.update(alteracoes)
        return dados

    def test_formulario_valido(self):
        form = FuncionarioForm(data=self.dados())
        self.assertTrue(form.is_valid(), form.errors)

    def test_unidade_cargo_e_data_sao_obrigatorios(self):
        form = FuncionarioForm(data=self.dados(unidade='', cargo='', data_admissao=''))
        self.assertFalse(form.is_valid())
        self.assertIn('unidade', form.errors)
        self.assertIn('cargo', form.errors)
        self.assertIn('data_admissao', form.errors)

    def test_cargo_inexistente_e_recusado(self):
        form = FuncionarioForm(data=self.dados(cargo='astronauta'))
        self.assertFalse(form.is_valid())
        self.assertIn('cargo', form.errors)

    def test_data_de_admissao_no_futuro_e_recusada(self):
        amanha = (date.today() + timedelta(days=2)).isoformat()
        form = FuncionarioForm(data=self.dados(data_admissao=amanha))
        self.assertFalse(form.is_valid())
        self.assertIn('A data de admissão não pode estar no futuro.', form.errors['data_admissao'])

    def test_listas_de_selecao_tem_texto_inicial(self):
        form = FuncionarioForm()
        self.assertEqual(form.fields['unidade'].empty_label, 'Selecione a unidade')
        self.assertEqual(form.fields['cargo'].choices[0], ('', 'Selecione o cargo'))
