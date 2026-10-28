from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from unidades.models import Unidade


class UnidadesSemLoginTests(TestCase):
    """Nenhuma página do módulo abre sem autenticação."""

    def test_paginas_redirecionam_para_o_login(self):
        unidade = Unidade.objects.create(nome='Unidade Centro', endereco='Rua A, 10')
        urls = [
            reverse('unidades_lista'),
            reverse('unidades_criar'),
            reverse('unidades_editar', args=[unidade.pk]),
            reverse('unidades_excluir', args=[unidade.pk]),
        ]
        for url in urls:
            with self.subTest(url=url):
                resposta = self.client.get(url)
                self.assertRedirects(resposta, f'/login/?next={url}')


class UnidadesViewsTests(TestCase):
    def setUp(self):
        usuario = get_user_model().objects.create_user(
            username='gerente',
            password='senha-de-teste-123',
        )
        self.client.force_login(usuario)
        self.unidade = Unidade.objects.create(
            nome='Unidade Centro',
            endereco='Rua A, 10',
            telefone='(31) 3333-0001',
        )

    def test_rotas_seguem_o_padrao_documentado(self):
        self.assertEqual(reverse('unidades_lista'), '/unidades/')
        self.assertEqual(reverse('unidades_criar'), '/unidades/novo/')
        self.assertEqual(reverse('unidades_editar', args=[7]), '/unidades/7/editar/')
        self.assertEqual(reverse('unidades_excluir', args=[7]), '/unidades/7/excluir/')

    def test_lista_mostra_as_unidades(self):
        resposta = self.client.get(reverse('unidades_lista'))
        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, 'unidades/lista.html')
        self.assertContains(resposta, 'Unidade Centro')
        self.assertContains(resposta, 'Rua A, 10')

    def test_lista_vazia_mostra_aviso(self):
        Unidade.objects.all().delete()
        resposta = self.client.get(reverse('unidades_lista'))
        self.assertContains(resposta, 'Nenhuma unidade cadastrada ainda.')

    def test_lista_e_paginada_de_10_em_10(self):
        for numero in range(1, 13):
            Unidade.objects.create(nome=f'Filial {numero:02d}', endereco='Rua B, 1')
        resposta = self.client.get(reverse('unidades_lista'))
        self.assertEqual(len(resposta.context['unidades']), 10)
        self.assertContains(resposta, 'Página 1 de 2')

        resposta = self.client.get(reverse('unidades_lista'), {'page': 2})
        self.assertEqual(len(resposta.context['unidades']), 3)

    def test_cadastro_cria_unidade_e_volta_para_a_lista(self):
        resposta = self.client.post(reverse('unidades_criar'), {
            'nome': 'Unidade Jardim',
            'endereco': 'Avenida B, 250',
            'telefone': '',
        }, follow=True)
        self.assertRedirects(resposta, reverse('unidades_lista'))
        self.assertTrue(Unidade.objects.filter(nome='Unidade Jardim').exists())
        self.assertContains(resposta, 'Unidade cadastrada com sucesso.')

    def test_cadastro_invalido_mostra_erros_e_nao_salva(self):
        resposta = self.client.post(reverse('unidades_criar'), {
            'nome': 'Unidade Centro',  # nome já existente
            'endereco': '',            # campo obrigatório vazio
        })
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, 'Já existe uma unidade com este nome.')
        self.assertContains(resposta, 'Este campo é obrigatório.')
        self.assertEqual(Unidade.objects.count(), 1)

    def test_edicao_abre_com_os_dados_atuais(self):
        resposta = self.client.get(reverse('unidades_editar', args=[self.unidade.pk]))
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, 'Editar unidade')
        self.assertContains(resposta, 'value="Unidade Centro"')

    def test_edicao_altera_a_unidade(self):
        resposta = self.client.post(reverse('unidades_editar', args=[self.unidade.pk]), {
            'nome': 'Unidade Centro Histórico',
            'endereco': 'Rua A, 10',
            'telefone': '(31) 3333-0001',
        }, follow=True)
        self.assertRedirects(resposta, reverse('unidades_lista'))
        self.unidade.refresh_from_db()
        self.assertEqual(self.unidade.nome, 'Unidade Centro Histórico')
        self.assertContains(resposta, 'Unidade atualizada com sucesso.')

    def test_exclusao_pede_confirmacao(self):
        resposta = self.client.get(reverse('unidades_excluir', args=[self.unidade.pk]))
        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, 'cadastros/confirmar_exclusao.html')
        self.assertContains(resposta, 'Unidade Centro')
        # Abrir a página de confirmação não remove nada.
        self.assertEqual(Unidade.objects.count(), 1)

    def test_exclusao_remove_a_unidade(self):
        resposta = self.client.post(
            reverse('unidades_excluir', args=[self.unidade.pk]),
            follow=True,
        )
        self.assertRedirects(resposta, reverse('unidades_lista'))
        self.assertEqual(Unidade.objects.count(), 0)
        self.assertContains(resposta, 'Unidade removida com sucesso.')

    def test_unidade_inexistente_retorna_404(self):
        resposta = self.client.get(reverse('unidades_editar', args=[9999]))
        self.assertEqual(resposta.status_code, 404)
