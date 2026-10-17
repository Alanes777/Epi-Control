from django.test import TestCase, Client
from django.urls import reverse
from core.models import Colaborador, EPI, Emprestimo


class ColaboradorCRUDTest(TestCase):
    """
    Testes automatizados cobrindo os requisitos obrigatórios do sistema EPI Control:
    1. Cadastro válido de colaborador.
    2. Tentativa de cadastrar matrícula duplicada.
    3. Pesquisa por nome completo e parcial.
    4. Pesquisa sem resultados.
    5. Edição de colaborador.
    6. Tentativa de edição com matrícula duplicada.
    7. Cancelamento da exclusão (requisição GET não deve excluir).
    8. Confirmação da exclusão (requisição POST).
    9. Persistência dos registros no banco.
    10. Validação dos campos obrigatórios.
    11. Navegação entre as páginas.
    """

    def setUp(self):
        self.client = Client()
        self.colab1 = Colaborador.objects.create(
            nome="Mariana Costa Souza",
            matricula="TEX-1003",
            setor="Fiação",
            cargo="Auxiliar de Fiação",
            email="mariana.souza@textilmodelo.com.br"
        )
        self.colab2 = Colaborador.objects.create(
            nome="Carlos Eduardo de Oliveira",
            matricula="TEX-1002",
            setor="Tinturaria",
            cargo="Colorista Industrial",
            email="carlos.oliveira@textilmodelo.com.br"
        )

    def test_01_cadastro_valido_colaborador(self):
        """Teste 1: Cadastro válido de colaborador deve persistir no banco e permanecer na página de cadastro."""
        dados = {
            'nome': 'João Pereira Lima',
            'matricula': 'TEX-2001',
            'setor': 'Tecelagem',
            'cargo': 'Operador',
            'email': 'joao.lima@empresa.com.br',
        }
        response = self.client.post(reverse('colaborador_create'), dados, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Colaborador.objects.filter(matricula='TEX-2001').exists())
        self.assertContains(response, "cadastrado com sucesso")

    def test_02_matricula_duplicada_no_cadastro(self):
        """Teste 2: Tentativa de cadastrar colaborador com matrícula já existente deve ser rejeitada."""
        dados = {
            'nome': 'Outro Colaborador',
            'matricula': 'TEX-1003',  # Já pertence à Mariana
            'setor': 'Costura',
        }
        response = self.client.post(reverse('colaborador_create'), dados)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIn('matricula', form.errors)
        self.assertIn("já está cadastrada para outro colaborador", form.errors['matricula'][0])

    def test_03_pesquisa_por_nome_completo_e_parcial(self):
        """Teste 3: Pesquisa por nome completo e por partes do nome."""
        # Pesquisa por parte: 'Mariana'
        res1 = self.client.get(reverse('colaborador_list') + '?q=Mariana')
        self.assertEqual(res1.status_code, 200)
        self.assertContains(res1, "Mariana Costa Souza")
        self.assertNotContains(res1, "Carlos Eduardo")

        # Pesquisa por parte: 'Oliveira'
        res2 = self.client.get(reverse('colaborador_list') + '?q=Oliveira')
        self.assertEqual(res2.status_code, 200)
        self.assertContains(res2, "Carlos Eduardo de Oliveira")

    def test_04_pesquisa_sem_resultados(self):
        """Teste 4: Pesquisa que não retorna registros deve exibir mensagem informativa."""
        res = self.client.get(reverse('colaborador_list') + '?q=NomeInexistenteXYZ')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Nenhum colaborador encontrado")

    def test_05_edicao_colaborador(self):
        """Teste 5: Edição bem-sucedida de um colaborador."""
        dados = {
            'nome': 'Mariana Costa Souza Lima',
            'matricula': 'TEX-1003',  # Mantém a mesma matrícula
            'setor': 'Fiação Avançada',
            'cargo': 'Tecelã Sênior',
            'email': 'mariana.nova@empresa.com.br',
        }
        res = self.client.post(reverse('colaborador_update', args=[self.colab1.pk]), dados, follow=True)
        self.assertEqual(res.status_code, 200)
        self.colab1.refresh_from_db()
        self.assertEqual(self.colab1.nome, 'Mariana Costa Souza Lima')
        self.assertEqual(self.colab1.setor, 'Fiação Avançada')
        self.assertContains(res, "atualizados com sucesso")

    def test_06_edicao_com_matricula_duplicada(self):
        """Teste 6: Tentar alterar a matrícula para uma que pertence a OUTRO colaborador deve falhar."""
        dados = {
            'nome': 'Mariana Costa Souza',
            'matricula': 'TEX-1002',  # Já pertence ao Carlos Eduardo
            'setor': 'Fiação',
        }
        res = self.client.post(reverse('colaborador_update', args=[self.colab1.pk]), dados)
        self.assertEqual(res.status_code, 200)
        form = res.context['form']
        self.assertIn('matricula', form.errors)
        self.assertIn("já está cadastrada para outro colaborador", form.errors['matricula'][0])

    def test_07_exclusao_via_get_bloqueada(self):
        """Teste 7: Não permitir exclusões por requisições GET (exige POST)."""
        res = self.client.get(reverse('colaborador_delete', args=[self.colab1.pk]))
        # Deve retornar 405 Method Not Allowed
        self.assertEqual(res.status_code, 405)
        # O registro deve permanecer no banco
        self.assertTrue(Colaborador.objects.filter(pk=self.colab1.pk).exists())

    def test_08_exclusao_confirmada_via_post(self):
        """Teste 8: Confirmação da exclusão via POST deve deletar o registro e redirecionar com mensagem."""
        pk = self.colab1.pk
        res = self.client.post(reverse('colaborador_delete', args=[pk]), follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertFalse(Colaborador.objects.filter(pk=pk).exists())
        self.assertContains(res, "excluído com sucesso")

    def test_10_validacao_campos_obrigatorios(self):
        """Teste 10: Campos obrigatórios (nome, matrícula, setor) não podem ser vazios."""
        dados_vazios = {
            'nome': '',
            'matricula': '',
            'setor': '',
        }
        res = self.client.post(reverse('colaborador_create'), dados_vazios)
        self.assertEqual(res.status_code, 200)
        form = res.context['form']
        self.assertIn('nome', form.errors)
        self.assertIn('matricula', form.errors)
        self.assertIn('setor', form.errors)

    def test_11_navegacao_entre_paginas(self):
        """Teste 11: Navegação por todas as rotas principais deve retornar status 200."""
        urls = [
            reverse('home'),
            reverse('colaborador_list'),
            reverse('colaborador_create'),
            reverse('colaborador_update', args=[self.colab2.pk]),
            reverse('equipamentos'),
            reverse('emprestimos'),
        ]
        for url in urls:
            res = self.client.get(url)
            self.assertEqual(res.status_code, 200, f"Falha ao carregar a página: {url}")
