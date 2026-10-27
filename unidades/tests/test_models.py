from django.db import IntegrityError
from django.test import TestCase

from unidades.forms import UnidadeForm
from unidades.models import Unidade


class UnidadeModelTests(TestCase):
    def test_texto_da_unidade_e_o_nome(self):
        unidade = Unidade.objects.create(nome='Unidade Centro', endereco='Rua A, 10')
        self.assertEqual(str(unidade), 'Unidade Centro')

    def test_unidades_sao_ordenadas_por_nome(self):
        Unidade.objects.create(nome='Unidade Sul', endereco='Rua B, 20')
        Unidade.objects.create(nome='Unidade Centro', endereco='Rua A, 10')
        nomes = list(Unidade.objects.values_list('nome', flat=True))
        self.assertEqual(nomes, ['Unidade Centro', 'Unidade Sul'])

    def test_nome_nao_pode_repetir(self):
        Unidade.objects.create(nome='Unidade Centro', endereco='Rua A, 10')
        with self.assertRaises(IntegrityError):
            Unidade.objects.create(nome='Unidade Centro', endereco='Rua C, 30')


class UnidadeFormTests(TestCase):
    def test_formulario_valido(self):
        form = UnidadeForm(data={
            'nome': 'Unidade Centro',
            'endereco': 'Rua A, 10',
            'telefone': '(31) 3333-0001',
        })
        self.assertTrue(form.is_valid())

    def test_telefone_e_opcional(self):
        form = UnidadeForm(data={'nome': 'Unidade Centro', 'endereco': 'Rua A, 10'})
        self.assertTrue(form.is_valid())

    def test_nome_e_endereco_sao_obrigatorios(self):
        form = UnidadeForm(data={'telefone': '(31) 3333-0001'})
        self.assertFalse(form.is_valid())
        self.assertIn('nome', form.errors)
        self.assertIn('endereco', form.errors)

    def test_nome_repetido_mostra_mensagem_em_portugues(self):
        Unidade.objects.create(nome='Unidade Centro', endereco='Rua A, 10')
        form = UnidadeForm(data={'nome': 'Unidade Centro', 'endereco': 'Rua C, 30'})
        self.assertFalse(form.is_valid())
        self.assertIn('Já existe uma unidade com este nome.', form.errors['nome'])

    def test_espacos_em_volta_do_nome_sao_removidos(self):
        form = UnidadeForm(data={'nome': '  Unidade Centro  ', 'endereco': 'Rua A, 10'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['nome'], 'Unidade Centro')
