from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from core.models import Colaborador, EPI, Emprestimo, ItemEmprestimo


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
        dados = {
            'nome': 'Outro Colaborador',
            'matricula': 'TEX-1003',
            'setor': 'Costura',
        }
        response = self.client.post(reverse('colaborador_create'), dados)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIn('matricula', form.errors)
        self.assertIn("já está cadastrada para outro colaborador", form.errors['matricula'][0])

    def test_03_pesquisa_por_nome_completo_e_parcial(self):
        res1 = self.client.get(reverse('colaborador_list') + '?q=Mariana')
        self.assertEqual(res1.status_code, 200)
        self.assertContains(res1, "Mariana Costa Souza")
        self.assertNotContains(res1, "Carlos Eduardo")

        res2 = self.client.get(reverse('colaborador_list') + '?q=Oliveira')
        self.assertEqual(res2.status_code, 200)
        self.assertContains(res2, "Carlos Eduardo de Oliveira")

    def test_04_pesquisa_sem_resultados(self):
        res = self.client.get(reverse('colaborador_list') + '?q=NomeInexistenteXYZ')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Nenhum colaborador encontrado")

    def test_05_edicao_colaborador(self):
        dados = {
            'nome': 'Mariana Costa Souza Lima',
            'matricula': 'TEX-1003',
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
        dados = {
            'nome': 'Mariana Costa Souza',
            'matricula': 'TEX-1002',
            'setor': 'Fiação',
        }
        res = self.client.post(reverse('colaborador_update', args=[self.colab1.pk]), dados)
        self.assertEqual(res.status_code, 200)
        form = res.context['form']
        self.assertIn('matricula', form.errors)
        self.assertIn("já está cadastrada para outro colaborador", form.errors['matricula'][0])

    def test_07_exclusao_via_get_bloqueada(self):
        res = self.client.get(reverse('colaborador_delete', args=[self.colab1.pk]))
        self.assertEqual(res.status_code, 405)
        self.assertTrue(Colaborador.objects.filter(pk=self.colab1.pk).exists())

    def test_08_exclusao_confirmada_via_post(self):
        pk = self.colab1.pk
        res = self.client.post(reverse('colaborador_delete', args=[pk]), follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertFalse(Colaborador.objects.filter(pk=pk).exists())
        self.assertContains(res, "excluído com sucesso")

    def test_10_validacao_campos_obrigatorios(self):
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
        urls = [
            reverse('home'),
            reverse('colaborador_list'),
            reverse('colaborador_create'),
            reverse('colaborador_update', args=[self.colab2.pk]),
            reverse('epi_list'),
            reverse('epi_create'),
            reverse('emprestimo_list'),
            reverse('emprestimo_create'),
        ]
        for url in urls:
            res = self.client.get(url)
            self.assertEqual(res.status_code, 200, f"Falha ao carregar a página: {url}")


class EPICRUDTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.epi1 = EPI.objects.create(
            nome="Protetor Auditivo Concha",
            certificado_aprovacao="5745",
            quantidade_estoque=30,
            descricao="Proteção auditiva para operadores de teares."
        )

    def test_cadastro_valido_epi(self):
        dados = {
            'nome': 'Máscara Facial P2',
            'certificado_aprovacao': '4115',
            'quantidade_estoque': 50,
            'descricao': 'Proteção contra poeira têxtil.',
        }
        res = self.client.post(reverse('epi_create'), dados, follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(EPI.objects.filter(nome='Máscara Facial P2').exists())
        self.assertContains(res, "cadastrado com sucesso")

    def test_estoque_negativo_rejeitado(self):
        dados = {
            'nome': 'Luva Nitrílica',
            'quantidade_estoque': -5,
        }
        res = self.client.post(reverse('epi_create'), dados)
        self.assertEqual(res.status_code, 200)
        form = res.context['form']
        self.assertIn('quantidade_estoque', form.errors)

    def test_pesquisa_epi_por_nome_e_ca(self):
        res1 = self.client.get(reverse('epi_list') + '?q=Concha')
        self.assertEqual(res1.status_code, 200)
        self.assertContains(res1, "Protetor Auditivo Concha")

        res2 = self.client.get(reverse('epi_list') + '?q=5745')
        self.assertEqual(res2.status_code, 200)
        self.assertContains(res2, "C.A. 5745")

    def test_edicao_epi(self):
        dados = {
            'nome': 'Protetor Auditivo Concha Plus',
            'certificado_aprovacao': '5745',
            'quantidade_estoque': 45,
            'descricao': 'Versão atualizada.',
        }
        res = self.client.post(reverse('epi_update', args=[self.epi1.pk]), dados, follow=True)
        self.assertEqual(res.status_code, 200)
        self.epi1.refresh_from_db()
        self.assertEqual(self.epi1.nome, 'Protetor Auditivo Concha Plus')
        self.assertEqual(self.epi1.quantidade_estoque, 45)
        self.assertContains(res, "atualizado com sucesso")

    def test_exclusao_epi_post_e_get(self):
        res_get = self.client.get(reverse('epi_delete', args=[self.epi1.pk]))
        self.assertEqual(res_get.status_code, 405)
        self.assertTrue(EPI.objects.filter(pk=self.epi1.pk).exists())

        res_post = self.client.post(reverse('epi_delete', args=[self.epi1.pk]), follow=True)
        self.assertEqual(res_post.status_code, 200)
        self.assertFalse(EPI.objects.filter(pk=self.epi1.pk).exists())
        self.assertContains(res_post, "excluído com sucesso")


class EmprestimoCRUDTest(TestCase):
    """
    Testes automatizados cobrindo Empréstimos e Devoluções (RF07 e RF09):
    - Registro de empréstimo com baixa automática de estoque
    - Bloqueio quando estoque é insuficiente
    - Consulta de empréstimos por colaborador e por período (RF07)
    - Devolução com reintegração de estoque
    - Exclusão via POST e bloqueio via GET
    """

    def setUp(self):
        self.client = Client()
        self.colab = Colaborador.objects.create(
            nome="Ana Paula da Silva",
            matricula="TEX-1001",
            setor="Tecelagem"
        )
        self.epi = EPI.objects.create(
            nome="Protetor Auditivo Concha",
            certificado_aprovacao="5745",
            quantidade_estoque=10
        )

    def test_registro_emprestimo_com_baixa_de_estoque(self):
        """RF09: Registro de empréstimo deve criar o vínculo e abater o estoque físico."""
        dados = {
            'colaborador': self.colab.pk,
            'epi': self.epi.pk,
            'quantidade': 3,
            'data_emprestimo': timezone.now().date().strftime('%Y-%m-%d'),
            'observacoes': 'Retirada para turno A',
        }
        res = self.client.post(reverse('emprestimo_create'), dados, follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(Emprestimo.objects.filter(colaborador=self.colab).exists())

        # Verifica baixa no estoque
        self.epi.refresh_from_db()
        self.assertEqual(self.epi.quantidade_estoque, 7)  # 10 - 3 = 7

    def test_bloqueio_estoque_insuficiente(self):
        """RF09: Tentar emprestar mais itens do que o disponível em estoque deve falhar."""
        dados = {
            'colaborador': self.colab.pk,
            'epi': self.epi.pk,
            'quantidade': 25,  # Disponível apenas 10
            'data_emprestimo': timezone.now().date().strftime('%Y-%m-%d'),
        }
        res = self.client.post(reverse('emprestimo_create'), dados)
        self.assertEqual(res.status_code, 200)
        form = res.context['form']
        self.assertIn('quantidade', form.errors)
        self.assertIn("Estoque insuficiente", form.errors['quantidade'][0])

    def test_consulta_por_colaborador_e_periodo(self):
        """RF07: Permitir consultar empréstimos por colaborador e período."""
        hoje = timezone.now().date()
        emp = Emprestimo.objects.create(
            colaborador=self.colab,
            data_emprestimo=hoje,
            status='ATIVO'
        )
        ItemEmprestimo.objects.create(emprestimo=emp, epi=self.epi, quantidade=1)

        # Filtro por colaborador
        res1 = self.client.get(reverse('emprestimo_list') + f'?colaborador={self.colab.pk}')
        self.assertEqual(res1.status_code, 200)
        self.assertContains(res1, "Ana Paula da Silva")

        # Filtro por período
        data_ini = (hoje - timedelta(days=2)).strftime('%Y-%m-%d')
        data_fim = (hoje + timedelta(days=2)).strftime('%Y-%m-%d')
        res2 = self.client.get(reverse('emprestimo_list') + f'?data_inicio={data_ini}&data_fim={data_fim}')
        self.assertEqual(res2.status_code, 200)
        self.assertContains(res2, "Ana Paula da Silva")

    def test_devolucao_com_reintegracao_ao_estoque(self):
        """RF09: Devolução deve atualizar status e devolver peças ao almoxarifado."""
        self.epi.quantidade_estoque = 5
        self.epi.save()

        emp = Emprestimo.objects.create(
            colaborador=self.colab,
            data_emprestimo=timezone.now().date(),
            status='ATIVO'
        )
        ItemEmprestimo.objects.create(emprestimo=emp, epi=self.epi, quantidade=2)

        # Registra devolução
        dados_dev = {
            'data_devolucao': timezone.now().date().strftime('%Y-%m-%d'),
            'retornar_ao_estoque': 'on',
            'observacoes_devolucao': 'Peças limpas e perfeitas',
        }
        res = self.client.post(reverse('emprestimo_devolver', args=[emp.pk]), dados_dev, follow=True)
        self.assertEqual(res.status_code, 200)

        emp.refresh_from_db()
        self.assertEqual(emp.status, 'DEVOLVIDO')

        # Estoque reinserido: 5 + 2 = 7
        self.epi.refresh_from_db()
        self.assertEqual(self.epi.quantidade_estoque, 7)

    def test_exclusao_emprestimo_post_e_get(self):
        emp = Emprestimo.objects.create(
            colaborador=self.colab,
            data_emprestimo=timezone.now().date(),
            status='ATIVO'
        )
        # GET bloqueado com 405
        res_get = self.client.get(reverse('emprestimo_delete', args=[emp.pk]))
        self.assertEqual(res_get.status_code, 405)
        self.assertTrue(Emprestimo.objects.filter(pk=emp.pk).exists())

        # POST exclui
        res_post = self.client.post(reverse('emprestimo_delete', args=[emp.pk]), follow=True)
        self.assertEqual(res_post.status_code, 200)
        self.assertFalse(Emprestimo.objects.filter(pk=emp.pk).exists())
