from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from fornecedores.models import Fornecedor


class FornecedoresSemLoginTests(TestCase):
    """Nenhuma página do módulo abre sem autenticação."""

    def test_paginas_redirecionam_para_o_login(self):
        fornecedor = Fornecedor.objects.create(razao_social='Moinho', cnpj='11222333000144')
        urls = [
            reverse('fornecedores_lista'),
            reverse('fornecedores_criar'),
            reverse('fornecedores_editar', args=[fornecedor.pk]),
            reverse('fornecedores_excluir', args=[fornecedor.pk]),
        ]
        for url in urls:
            with self.subTest(url=url):
                resposta = self.client.get(url)
                self.assertRedirects(resposta, f'/login/?next={url}')


class FornecedoresViewsTests(TestCase):
    def setUp(self):
        usuario = get_user_model().objects.create_user(
            username='gerente',
            password='senha-de-teste-123',
        )
        self.client.force_login(usuario)
        self.fornecedor = Fornecedor.objects.create(
            razao_social='Moinho Serra Azul Ltda',
            nome_fantasia='Farinhas Serra Azul',
            cnpj='11222333000144',
            contato='Roberto',
        )

    def test_rotas_seguem_o_padrao_documentado(self):
        self.assertEqual(reverse('fornecedores_lista'), '/fornecedores/')
        self.assertEqual(reverse('fornecedores_criar'), '/fornecedores/novo/')
        self.assertEqual(reverse('fornecedores_editar', args=[7]), '/fornecedores/7/editar/')
        self.assertEqual(reverse('fornecedores_excluir', args=[7]), '/fornecedores/7/excluir/')

    def test_lista_mostra_fornecedor_com_cnpj_formatado(self):
        resposta = self.client.get(reverse('fornecedores_lista'))
        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, 'fornecedores/lista.html')
        self.assertContains(resposta, 'Moinho Serra Azul Ltda')
        self.assertContains(resposta, 'Farinhas Serra Azul')
        self.assertContains(resposta, '11.222.333/0001-44')

    def test_lista_vazia_mostra_aviso(self):
        Fornecedor.objects.all().delete()
        resposta = self.client.get(reverse('fornecedores_lista'))
        self.assertContains(resposta, 'Nenhum fornecedor cadastrado ainda.')

    def test_busca_por_nome(self):
        Fornecedor.objects.create(razao_social='Embalagens Bom Pão', cnpj='22333444000155')
        resposta = self.client.get(reverse('fornecedores_lista'), {'q': 'embalagens'})
        self.assertContains(resposta, 'Embalagens Bom Pão')
        self.assertNotContains(resposta, 'Moinho Serra Azul Ltda')

    def test_busca_por_cnpj_com_pontuacao(self):
        Fornecedor.objects.create(razao_social='Embalagens Bom Pão', cnpj='22333444000155')
        resposta = self.client.get(reverse('fornecedores_lista'), {'q': '11.222.333'})
        self.assertContains(resposta, 'Moinho Serra Azul Ltda')
        self.assertNotContains(resposta, 'Embalagens Bom Pão')

    def test_busca_sem_resultado_mostra_aviso(self):
        resposta = self.client.get(reverse('fornecedores_lista'), {'q': 'inexistente'})
        self.assertContains(resposta, 'Nenhum fornecedor encontrado para')

    def test_paginacao_mantem_a_busca(self):
        for numero in range(1, 13):
            Fornecedor.objects.create(
                razao_social=f'Laticínios {numero:02d}',
                cnpj=f'{numero:014d}',
            )
        resposta = self.client.get(reverse('fornecedores_lista'), {'q': 'laticínios'})
        self.assertContains(resposta, 'Página 1 de 2')
        self.assertContains(resposta, '?page=2&amp;q=latic')

    def test_cadastro_cria_fornecedor_e_volta_para_a_lista(self):
        resposta = self.client.post(reverse('fornecedores_criar'), {
            'razao_social': 'Embalagens Bom Pão Ltda',
            'cnpj': '22.333.444/0001-55',
        }, follow=True)
        self.assertRedirects(resposta, reverse('fornecedores_lista'))
        fornecedor = Fornecedor.objects.get(razao_social='Embalagens Bom Pão Ltda')
        self.assertEqual(fornecedor.cnpj, '22333444000155')
        self.assertContains(resposta, 'Fornecedor cadastrado com sucesso.')

    def test_cadastro_com_cnpj_invalido_mostra_erro_e_nao_salva(self):
        resposta = self.client.post(reverse('fornecedores_criar'), {
            'razao_social': 'Empresa Teste',
            'cnpj': '123',
        })
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, 'Informe um CNPJ com 14 dígitos.')
        self.assertEqual(Fornecedor.objects.count(), 1)

    def test_edicao_abre_com_cnpj_formatado(self):
        resposta = self.client.get(reverse('fornecedores_editar', args=[self.fornecedor.pk]))
        self.assertContains(resposta, 'Editar fornecedor')
        self.assertContains(resposta, 'value="11.222.333/0001-44"')

    def test_edicao_altera_o_fornecedor(self):
        resposta = self.client.post(reverse('fornecedores_editar', args=[self.fornecedor.pk]), {
            'razao_social': 'Moinho Serra Azul Ltda',
            'cnpj': '11.222.333/0001-44',
            'contato': 'Ana Paula',
        }, follow=True)
        self.assertRedirects(resposta, reverse('fornecedores_lista'))
        self.fornecedor.refresh_from_db()
        self.assertEqual(self.fornecedor.contato, 'Ana Paula')
        self.assertContains(resposta, 'Fornecedor atualizado com sucesso.')

    def test_exclusao_pede_confirmacao_e_remove(self):
        url = reverse('fornecedores_excluir', args=[self.fornecedor.pk])
        resposta = self.client.get(url)
        self.assertTemplateUsed(resposta, 'cadastros/confirmar_exclusao.html')
        self.assertEqual(Fornecedor.objects.count(), 1)

        resposta = self.client.post(url, follow=True)
        self.assertRedirects(resposta, reverse('fornecedores_lista'))
        self.assertEqual(Fornecedor.objects.count(), 0)
        self.assertContains(resposta, 'Fornecedor removido com sucesso.')
