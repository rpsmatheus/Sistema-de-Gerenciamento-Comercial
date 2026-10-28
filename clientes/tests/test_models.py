from django.test import TestCase

from clientes.forms import ClienteForm
from clientes.models import Cliente


class ClienteModelTests(TestCase):
    def test_texto_do_cliente_e_o_nome(self):
        cliente = Cliente.objects.create(nome='Maria Souza', documento='12345678901')
        self.assertEqual(str(cliente), 'Maria Souza')

    def test_cpf_e_formatado_com_pontuacao(self):
        cliente = Cliente(nome='Maria Souza', documento='12345678901')
        self.assertEqual(cliente.tipo_documento, 'CPF')
        self.assertEqual(cliente.documento_formatado, '123.456.789-01')

    def test_cnpj_e_formatado_com_pontuacao(self):
        cliente = Cliente(nome='Café da Praça', documento='12345678000190')
        self.assertEqual(cliente.tipo_documento, 'CNPJ')
        self.assertEqual(cliente.documento_formatado, '12.345.678/0001-90')

    def test_clientes_sao_ordenados_por_nome(self):
        Cliente.objects.create(nome='Maria Souza', documento='12345678901')
        Cliente.objects.create(nome='Ana Lima', documento='98765432100')
        nomes = list(Cliente.objects.values_list('nome', flat=True))
        self.assertEqual(nomes, ['Ana Lima', 'Maria Souza'])


class ClienteFormTests(TestCase):
    def dados(self, **alteracoes):
        dados = {
            'nome': 'Maria Souza',
            'documento': '123.456.789-01',
            'telefone': '(31) 99999-0001',
            'email': 'maria@exemplo.com',
            'endereco': 'Rua A, 10',
        }
        dados.update(alteracoes)
        return dados

    def test_formulario_valido(self):
        form = ClienteForm(data=self.dados())
        self.assertTrue(form.is_valid())

    def test_documento_e_salvo_somente_com_numeros(self):
        form = ClienteForm(data=self.dados())
        self.assertTrue(form.is_valid())
        cliente = form.save()
        self.assertEqual(cliente.documento, '12345678901')

    def test_cnpj_com_pontuacao_e_aceito(self):
        form = ClienteForm(data=self.dados(documento='12.345.678/0001-90'))
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['documento'], '12345678000190')

    def test_documento_com_tamanho_errado_e_recusado(self):
        form = ClienteForm(data=self.dados(documento='12345'))
        self.assertFalse(form.is_valid())
        self.assertIn('documento', form.errors)

    def test_documento_repetido_e_recusado(self):
        Cliente.objects.create(nome='Outra Pessoa', documento='12345678901')
        form = ClienteForm(data=self.dados())
        self.assertFalse(form.is_valid())
        self.assertIn('Já existe um cliente com este CPF ou CNPJ.', form.errors['documento'])

    def test_editar_o_proprio_cliente_nao_acusa_documento_repetido(self):
        cliente = Cliente.objects.create(nome='Maria Souza', documento='12345678901')
        form = ClienteForm(data=self.dados(nome='Maria S. Lima'), instance=cliente)
        self.assertTrue(form.is_valid())

    def test_edicao_mostra_documento_com_pontuacao(self):
        cliente = Cliente.objects.create(nome='Maria Souza', documento='12345678901')
        form = ClienteForm(instance=cliente)
        self.assertEqual(form.initial['documento'], '123.456.789-01')

    def test_somente_nome_e_documento_sao_obrigatorios(self):
        form = ClienteForm(data={'nome': 'Maria Souza', 'documento': '12345678901'})
        self.assertTrue(form.is_valid())

    def test_email_invalido_e_recusado(self):
        form = ClienteForm(data=self.dados(email='nao-e-email'))
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
