from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from funcionarios.models import Funcionario
from unidades.models import Unidade


class FuncionariosSemLoginTests(TestCase):
    """Nenhuma página do módulo abre sem autenticação."""

    def test_paginas_redirecionam_para_o_login(self):
        unidade = Unidade.objects.create(nome='Unidade Centro', endereco='Rua A, 10')
        funcionario = Funcionario.objects.create(
            nome='João Silva', unidade=unidade, cargo='padeiro', data_admissao=date(2025, 3, 1),
        )
        urls = [
            reverse('funcionarios_lista'),
            reverse('funcionarios_criar'),
            reverse('funcionarios_editar', args=[funcionario.pk]),
            reverse('funcionarios_excluir', args=[funcionario.pk]),
        ]
        for url in urls:
            with self.subTest(url=url):
                resposta = self.client.get(url)
                self.assertRedirects(resposta, f'/login/?next={url}')


class FuncionariosViewsTests(TestCase):
    def setUp(self):
        usuario = get_user_model().objects.create_user(
            username='gerente',
            password='senha-de-teste-123',
        )
        self.client.force_login(usuario)
        self.centro = Unidade.objects.create(nome='Unidade Centro', endereco='Rua A, 10')
        self.jardim = Unidade.objects.create(nome='Unidade Jardim', endereco='Rua B, 20')
        self.joao = Funcionario.objects.create(
            nome='João Silva', unidade=self.centro, cargo='padeiro',
            data_admissao=date(2025, 3, 1),
        )
        self.ana = Funcionario.objects.create(
            nome='Ana Souza', unidade=self.jardim, cargo='atendente',
            data_admissao=date(2024, 6, 10), situacao='inativo',
        )

    def dados(self, **alteracoes):
        dados = {
            'nome': 'Carla Dias',
            'unidade': self.centro.pk,
            'cargo': 'confeiteiro',
            'telefone': '',
            'email': '',
            'data_admissao': '2025-01-15',
            'situacao': 'ativo',
        }
        dados.update(alteracoes)
        return dados

    def test_rotas_seguem_o_padrao_documentado(self):
        self.assertEqual(reverse('funcionarios_lista'), '/funcionarios/')
        self.assertEqual(reverse('funcionarios_criar'), '/funcionarios/novo/')
        self.assertEqual(reverse('funcionarios_editar', args=[7]), '/funcionarios/7/editar/')
        self.assertEqual(reverse('funcionarios_excluir', args=[7]), '/funcionarios/7/excluir/')

    def test_lista_mostra_cargo_unidade_e_situacao(self):
        resposta = self.client.get(reverse('funcionarios_lista'))
        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, 'funcionarios/lista.html')
        self.assertContains(resposta, 'João Silva')
        self.assertContains(resposta, 'Padeiro(a)')
        self.assertContains(resposta, 'Unidade Centro')
        self.assertContains(resposta, 'Desde 01/03/2025')
        self.assertContains(resposta, 'Inativo')

    def test_lista_sem_unidades_orienta_cadastrar_unidade(self):
        Funcionario.objects.all().delete()
        Unidade.objects.all().delete()
        resposta = self.client.get(reverse('funcionarios_lista'))
        self.assertContains(resposta, 'cadastre antes uma unidade')

    def test_busca_por_nome(self):
        resposta = self.client.get(reverse('funcionarios_lista'), {'q': 'ana'})
        self.assertEqual(list(resposta.context['funcionarios']), [self.ana])

    def test_filtro_por_unidade(self):
        resposta = self.client.get(reverse('funcionarios_lista'), {'unidade': self.centro.pk})
        self.assertEqual(list(resposta.context['funcionarios']), [self.joao])
        self.assertContains(resposta, f'value="{self.centro.pk}" selected')

    def test_filtro_por_situacao(self):
        resposta = self.client.get(reverse('funcionarios_lista'), {'situacao': 'ativo'})
        self.assertEqual(list(resposta.context['funcionarios']), [self.joao])

    def test_filtros_combinados_sem_resultado_mostram_aviso(self):
        resposta = self.client.get(
            reverse('funcionarios_lista'),
            {'unidade': self.centro.pk, 'situacao': 'inativo'},
        )
        self.assertContains(resposta, 'Nenhum funcionário encontrado com estes filtros.')

    def test_filtros_invalidos_sao_ignorados(self):
        resposta = self.client.get(
            reverse('funcionarios_lista'),
            {'unidade': 'abc', 'situacao': 'qualquer'},
        )
        self.assertEqual(len(resposta.context['funcionarios']), 2)

    def test_paginacao_mantem_os_filtros(self):
        for numero in range(1, 13):
            Funcionario.objects.create(
                nome=f'Auxiliar {numero:02d}', unidade=self.centro, cargo='auxiliar',
                data_admissao=date(2025, 1, 1),
            )
        resposta = self.client.get(
            reverse('funcionarios_lista'),
            {'unidade': self.centro.pk, 'situacao': 'ativo'},
        )
        self.assertContains(resposta, 'Página 1 de 2')
        self.assertContains(resposta, f'?page=2&amp;unidade={self.centro.pk}&amp;situacao=ativo')

    def test_cadastro_cria_funcionario_e_volta_para_a_lista(self):
        resposta = self.client.post(reverse('funcionarios_criar'), self.dados(), follow=True)
        self.assertRedirects(resposta, reverse('funcionarios_lista'))
        funcionario = Funcionario.objects.get(nome='Carla Dias')
        self.assertEqual(funcionario.unidade, self.centro)
        self.assertContains(resposta, 'Funcionário cadastrado com sucesso.')

    def test_cadastro_sem_unidade_mostra_erro_e_nao_salva(self):
        resposta = self.client.post(reverse('funcionarios_criar'), self.dados(unidade=''))
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, 'Este campo é obrigatório.')
        self.assertEqual(Funcionario.objects.count(), 2)

    def test_formulario_lista_as_unidades(self):
        resposta = self.client.get(reverse('funcionarios_criar'))
        self.assertContains(resposta, 'Selecione a unidade')
        self.assertContains(resposta, 'Unidade Jardim')
        self.assertContains(resposta, 'type="date"')

    def test_edicao_abre_com_os_dados_atuais(self):
        resposta = self.client.get(reverse('funcionarios_editar', args=[self.joao.pk]))
        self.assertContains(resposta, 'Editar funcionário')
        self.assertContains(resposta, 'value="2025-03-01"')

    def test_edicao_transfere_funcionario_de_unidade(self):
        dados = self.dados(nome='João Silva', unidade=self.jardim.pk, cargo='padeiro',
                           data_admissao='2025-03-01')
        resposta = self.client.post(
            reverse('funcionarios_editar', args=[self.joao.pk]), dados, follow=True,
        )
        self.assertRedirects(resposta, reverse('funcionarios_lista'))
        self.joao.refresh_from_db()
        self.assertEqual(self.joao.unidade, self.jardim)
        self.assertContains(resposta, 'Funcionário atualizado com sucesso.')

    def test_exclusao_pede_confirmacao_e_remove(self):
        url = reverse('funcionarios_excluir', args=[self.joao.pk])
        resposta = self.client.get(url)
        self.assertTemplateUsed(resposta, 'cadastros/confirmar_exclusao.html')
        self.assertContains(resposta, 'João Silva')

        resposta = self.client.post(url, follow=True)
        self.assertRedirects(resposta, reverse('funcionarios_lista'))
        self.assertFalse(Funcionario.objects.filter(pk=self.joao.pk).exists())
        self.assertContains(resposta, 'Funcionário removido com sucesso.')
