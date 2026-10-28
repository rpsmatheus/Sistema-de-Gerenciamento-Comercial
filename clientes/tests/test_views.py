from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from clientes.models import Cliente


class ClientesSemLoginTests(TestCase):
    """Nenhuma página do módulo abre sem autenticação."""

    def test_paginas_redirecionam_para_o_login(self):
        cliente = Cliente.objects.create(nome='Maria Souza', documento='12345678901')
        urls = [
            reverse('clientes_lista'),
            reverse('clientes_criar'),
            reverse('clientes_editar', args=[cliente.pk]),
            reverse('clientes_excluir', args=[cliente.pk]),
        ]
        for url in urls:
            with self.subTest(url=url):
                resposta = self.client.get(url)
                self.assertRedirects(resposta, f'/login/?next={url}')


class ClientesViewsTests(TestCase):
    def setUp(self):
        usuario = get_user_model().objects.create_user(
            username='gerente',
            password='senha-de-teste-123',
        )
        self.client.force_login(usuario)
        self.cliente = Cliente.objects.create(
            nome='Maria Souza',
            documento='12345678901',
            telefone='(31) 99999-0001',
            email='maria@exemplo.com',
        )

    def test_rotas_seguem_o_padrao_documentado(self):
        self.assertEqual(reverse('clientes_lista'), '/clientes/')
        self.assertEqual(reverse('clientes_criar'), '/clientes/novo/')
        self.assertEqual(reverse('clientes_editar', args=[7]), '/clientes/7/editar/')
        self.assertEqual(reverse('clientes_excluir', args=[7]), '/clientes/7/excluir/')

    def test_lista_mostra_os_clientes_com_documento_formatado(self):
        resposta = self.client.get(reverse('clientes_lista'))
        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, 'clientes/lista.html')
        self.assertContains(resposta, 'Maria Souza')
        self.assertContains(resposta, '123.456.789-01')

    def test_lista_vazia_mostra_aviso(self):
        Cliente.objects.all().delete()
        resposta = self.client.get(reverse('clientes_lista'))
        self.assertContains(resposta, 'Nenhum cliente cadastrado ainda.')

    def test_lista_e_paginada_de_10_em_10(self):
        for numero in range(1, 13):
            Cliente.objects.create(
                nome=f'Cliente {numero:02d}',
                documento=f'{numero:011d}',
            )
        resposta = self.client.get(reverse('clientes_lista'))
        self.assertEqual(len(resposta.context['clientes']), 10)
        self.assertContains(resposta, 'Página 1 de 2')

        resposta = self.client.get(reverse('clientes_lista'), {'page': 2})
        self.assertEqual(len(resposta.context['clientes']), 3)

    def test_cadastro_cria_cliente_e_volta_para_a_lista(self):
        resposta = self.client.post(reverse('clientes_criar'), {
            'nome': 'Café da Praça',
            'documento': '12.345.678/0001-90',
            'telefone': '',
            'email': '',
            'endereco': '',
        }, follow=True)
        self.assertRedirects(resposta, reverse('clientes_lista'))
        cliente = Cliente.objects.get(nome='Café da Praça')
        self.assertEqual(cliente.documento, '12345678000190')
        self.assertContains(resposta, 'Cliente cadastrado com sucesso.')

    def test_cadastro_com_documento_invalido_mostra_erro_e_nao_salva(self):
        resposta = self.client.post(reverse('clientes_criar'), {
            'nome': 'João Lima',
            'documento': '123',
        })
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, 'Informe um CPF com 11 dígitos ou um CNPJ com 14 dígitos.')
        self.assertEqual(Cliente.objects.count(), 1)

    def test_cadastro_com_documento_repetido_mostra_erro(self):
        resposta = self.client.post(reverse('clientes_criar'), {
            'nome': 'Outra Maria',
            'documento': '123.456.789-01',
        })
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, 'Já existe um cliente com este CPF ou CNPJ.')
        self.assertEqual(Cliente.objects.count(), 1)

    def test_edicao_abre_com_os_dados_atuais(self):
        resposta = self.client.get(reverse('clientes_editar', args=[self.cliente.pk]))
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, 'Editar cliente')
        self.assertContains(resposta, 'value="Maria Souza"')
        self.assertContains(resposta, 'value="123.456.789-01"')

    def test_edicao_altera_o_cliente(self):
        resposta = self.client.post(reverse('clientes_editar', args=[self.cliente.pk]), {
            'nome': 'Maria Souza Lima',
            'documento': '123.456.789-01',
            'telefone': '(31) 99999-0001',
            'email': 'maria@exemplo.com',
            'endereco': 'Rua A, 10',
        }, follow=True)
        self.assertRedirects(resposta, reverse('clientes_lista'))
        self.cliente.refresh_from_db()
        self.assertEqual(self.cliente.nome, 'Maria Souza Lima')
        self.assertEqual(self.cliente.endereco, 'Rua A, 10')
        self.assertContains(resposta, 'Cliente atualizado com sucesso.')

    def test_exclusao_pede_confirmacao(self):
        resposta = self.client.get(reverse('clientes_excluir', args=[self.cliente.pk]))
        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, 'cadastros/confirmar_exclusao.html')
        self.assertContains(resposta, 'Maria Souza')
        # Abrir a página de confirmação não remove nada.
        self.assertEqual(Cliente.objects.count(), 1)

    def test_exclusao_remove_o_cliente(self):
        resposta = self.client.post(
            reverse('clientes_excluir', args=[self.cliente.pk]),
            follow=True,
        )
        self.assertRedirects(resposta, reverse('clientes_lista'))
        self.assertEqual(Cliente.objects.count(), 0)
        self.assertContains(resposta, 'Cliente removido com sucesso.')

    def test_cliente_inexistente_retorna_404(self):
        resposta = self.client.get(reverse('clientes_editar', args=[9999]))
        self.assertEqual(resposta.status_code, 404)
