from django.test import TestCase

from fornecedores.forms import FornecedorForm
from fornecedores.models import Fornecedor


class FornecedorModelTests(TestCase):
    def test_texto_usa_nome_fantasia_quando_existe(self):
        fornecedor = Fornecedor(
            razao_social='Moinho Serra Azul Ltda',
            nome_fantasia='Farinhas Serra Azul',
            cnpj='11222333000144',
        )
        self.assertEqual(str(fornecedor), 'Farinhas Serra Azul')

    def test_texto_usa_razao_social_sem_nome_fantasia(self):
        fornecedor = Fornecedor(razao_social='Moinho Serra Azul Ltda', cnpj='11222333000144')
        self.assertEqual(str(fornecedor), 'Moinho Serra Azul Ltda')

    def test_cnpj_e_formatado_com_pontuacao(self):
        fornecedor = Fornecedor(razao_social='Moinho', cnpj='11222333000144')
        self.assertEqual(fornecedor.cnpj_formatado, '11.222.333/0001-44')

    def test_fornecedores_sao_ordenados_por_razao_social(self):
        Fornecedor.objects.create(razao_social='Zeta Embalagens', cnpj='11111111000111')
        Fornecedor.objects.create(razao_social='Alfa Laticínios', cnpj='22222222000122')
        nomes = list(Fornecedor.objects.values_list('razao_social', flat=True))
        self.assertEqual(nomes, ['Alfa Laticínios', 'Zeta Embalagens'])


class FornecedorFormTests(TestCase):
    def dados(self, **alteracoes):
        dados = {
            'razao_social': 'Moinho Serra Azul Ltda',
            'nome_fantasia': 'Farinhas Serra Azul',
            'cnpj': '11.222.333/0001-44',
            'contato': 'Roberto',
            'telefone': '(31) 3333-2001',
            'email': 'vendas@serraazul.exemplo.com',
            'observacoes': 'Entrega às segundas.',
        }
        dados.update(alteracoes)
        return dados

    def test_formulario_valido(self):
        form = FornecedorForm(data=self.dados())
        self.assertTrue(form.is_valid())

    def test_cnpj_e_salvo_somente_com_numeros(self):
        form = FornecedorForm(data=self.dados())
        self.assertTrue(form.is_valid())
        fornecedor = form.save()
        self.assertEqual(fornecedor.cnpj, '11222333000144')

    def test_cnpj_com_tamanho_errado_e_recusado(self):
        form = FornecedorForm(data=self.dados(cnpj='123.456.789-01'))
        self.assertFalse(form.is_valid())
        self.assertIn('Informe um CNPJ com 14 dígitos.', form.errors['cnpj'])

    def test_cnpj_repetido_e_recusado(self):
        Fornecedor.objects.create(razao_social='Outro', cnpj='11222333000144')
        form = FornecedorForm(data=self.dados())
        self.assertFalse(form.is_valid())
        self.assertIn('Já existe um fornecedor com este CNPJ.', form.errors['cnpj'])

    def test_editar_o_proprio_fornecedor_nao_acusa_cnpj_repetido(self):
        fornecedor = Fornecedor.objects.create(razao_social='Moinho', cnpj='11222333000144')
        form = FornecedorForm(data=self.dados(contato='Ana'), instance=fornecedor)
        self.assertTrue(form.is_valid())

    def test_edicao_mostra_cnpj_com_pontuacao(self):
        fornecedor = Fornecedor.objects.create(razao_social='Moinho', cnpj='11222333000144')
        form = FornecedorForm(instance=fornecedor)
        self.assertEqual(form.initial['cnpj'], '11.222.333/0001-44')

    def test_somente_razao_social_e_cnpj_sao_obrigatorios(self):
        form = FornecedorForm(data={'razao_social': 'Moinho', 'cnpj': '11222333000144'})
        self.assertTrue(form.is_valid())
