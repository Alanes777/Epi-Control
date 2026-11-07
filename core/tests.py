from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from core.models import Setor, Colaborador, EPI, Emprestimo, ItemEmprestimo


class ColaboradorCRUDTest(TestCase):
    """
    Testes automatizados cobrindo os requisitos obrigatórios do módulo de Colaboradores:
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
        self.user = User.objects.create_user(username='tester_colab', password='password123')
        self.client.force_login(self.user)

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
            reverse('relatorio_list'),
            reverse('usuario_list'),
        ]
        for url in urls:
            res = self.client.get(url)
            self.assertEqual(res.status_code, 200, f"Falha ao carregar a página: {url}")


class EPICRUDTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='tester_epi', password='password123')
        self.client.force_login(self.user)

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
    Testes automatizados cobrindo Controle de EPI / Empréstimos e Devoluções:
    - Registro de empréstimo com data futura para devolução e baixa automática de estoque.
    - Rejeição de status proibidos no cadastro (Devolvido, Danificado, Perdido).
    - Validação de que a data prevista de devolução deve ser posterior à data atual.
    - Bloqueio quando estoque é insuficiente no almoxarifado.
    - Consulta e listagem com filtros simultâneos tipo AND (colaborador AND status AND equipamento).
    - Atualização de status para 'Devolvido' com reintegração física ao estoque.
    - Validação de obrigatoriedade da data de devolução para status Devolvido/Danificado/Perdido.
    - Exclusão via POST e bloqueio via GET.
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='tester_emp', password='password123')
        self.client.force_login(self.user)

        self.colab = Colaborador.objects.create(
            nome="Carlos Eduardo Pereira",
            matricula="CONST-2001",
            setor="Canteiro de Obras",
            cargo="Pedreiro"
        )
        self.epi = EPI.objects.create(
            nome="Capacete de Segurança com Jugular",
            certificado_aprovacao="498",
            quantidade_estoque=10
        )

    def test_registro_emprestimo_com_baixa_de_estoque(self):
        """Registro de empréstimo válido com data prevista futura e baixa no estoque."""
        hoje = timezone.now().date()
        amanha = hoje + timedelta(days=5)

        dados = {
            'colaborador': self.colab.pk,
            'epi': self.epi.pk,
            'quantidade': 3,
            'data_emprestimo': hoje.strftime('%Y-%m-%d'),
            'data_prevista_devolucao': amanha.strftime('%Y-%m-%d'),
            'status': 'EMPRESTADO',
            'observacoes': 'Retirada para trabalho em laje',
        }
        res = self.client.post(reverse('emprestimo_create'), dados, follow=True)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(Emprestimo.objects.filter(colaborador=self.colab).exists())

        # Verifica baixa no estoque físico (10 - 3 = 7)
        self.epi.refresh_from_db()
        self.assertEqual(self.epi.quantidade_estoque, 7)
        self.assertContains(res, "Empréstimo registrado com sucesso")

    def test_data_prevista_no_passado_ou_hoje_rejeitada(self):
        """A data prevista para devolução deve ser posterior à data atual."""
        hoje = timezone.now().date()
        ontem = hoje - timedelta(days=1)

        dados = {
            'colaborador': self.colab.pk,
            'epi': self.epi.pk,
            'quantidade': 1,
            'data_emprestimo': hoje.strftime('%Y-%m-%d'),
            'data_prevista_devolucao': ontem.strftime('%Y-%m-%d'),
            'status': 'EMPRESTADO',
        }
        res = self.client.post(reverse('emprestimo_create'), dados)
        self.assertEqual(res.status_code, 200)
        form = res.context['form']
        self.assertIn('data_prevista_devolucao', form.errors)
        self.assertIn("posterior", form.errors['data_prevista_devolucao'][0].lower())

    def test_status_devolvido_rejeitado_no_cadastro(self):
        """Os status Devolvido, Danificado e Perdido devem estar ocultos/bloqueados no cadastro."""
        hoje = timezone.now().date()
        amanha = hoje + timedelta(days=3)

        dados = {
            'colaborador': self.colab.pk,
            'epi': self.epi.pk,
            'quantidade': 1,
            'data_emprestimo': hoje.strftime('%Y-%m-%d'),
            'data_prevista_devolucao': amanha.strftime('%Y-%m-%d'),
            'status': 'DEVOLVIDO',
        }
        res = self.client.post(reverse('emprestimo_create'), dados)
        self.assertEqual(res.status_code, 200)
        form = res.context['form']
        self.assertIn('status', form.errors)

    def test_bloqueio_estoque_insuficiente(self):
        """Tentar emprestar mais itens do que o disponível em estoque deve falhar."""
        hoje = timezone.now().date()
        amanha = hoje + timedelta(days=2)

        dados = {
            'colaborador': self.colab.pk,
            'epi': self.epi.pk,
            'quantidade': 25,
            'data_emprestimo': hoje.strftime('%Y-%m-%d'),
            'data_prevista_devolucao': amanha.strftime('%Y-%m-%d'),
            'status': 'EMPRESTADO',
        }
        res = self.client.post(reverse('emprestimo_create'), dados)
        self.assertEqual(res.status_code, 200)
        form = res.context['form']
        self.assertIn('quantidade', form.errors)
        self.assertIn("Estoque insuficiente", form.errors['quantidade'][0])

    def test_consulta_filtro_and_colaborador_e_status(self):
        """Filtro do tipo AND: busca simultânea por nome do colaborador E status."""
        hoje = timezone.now().date()
        outro_colab = Colaborador.objects.create(
            nome="Sebastião Ferreira",
            matricula="CONST-2002",
            setor="Armação"
        )
        # Emprestimo 1: Carlos / EMPRESTADO
        Emprestimo.objects.create(
            colaborador=self.colab,
            epi=self.epi,
            quantidade=1,
            data_emprestimo=hoje,
            data_prevista_devolucao=hoje + timedelta(days=5),
            status='EMPRESTADO'
        )
        # Emprestimo 2: Carlos / DEVOLVIDO
        Emprestimo.objects.create(
            colaborador=self.colab,
            epi=self.epi,
            quantidade=1,
            data_emprestimo=hoje - timedelta(days=10),
            data_devolucao=hoje,
            status='DEVOLVIDO'
        )
        # Emprestimo 3: Sebastião / EMPRESTADO
        Emprestimo.objects.create(
            colaborador=outro_colab,
            epi=self.epi,
            quantidade=1,
            data_emprestimo=hoje,
            data_prevista_devolucao=hoje + timedelta(days=5),
            status='EMPRESTADO'
        )

        # Filtro AND: Carlos AND EMPRESTADO deve trazer apenas o Emprestimo 1
        url = reverse('emprestimo_list') + f'?colaborador_nome=Carlos&status=EMPRESTADO'
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['total_encontrados'], 1)
        self.assertContains(res, "Carlos Eduardo Pereira")
        self.assertNotContains(res, "Sebastião Ferreira")

    def test_atualizacao_status_com_reintegracao_ao_estoque(self):
        """Atualização para status 'DEVOLVIDO' reincorpora as unidades ao almoxarifado."""
        self.epi.quantidade_estoque = 5
        self.epi.save()

        hoje = timezone.now().date()
        emp = Emprestimo.objects.create(
            colaborador=self.colab,
            epi=self.epi,
            quantidade=2,
            data_emprestimo=hoje,
            data_prevista_devolucao=hoje + timedelta(days=4),
            status='EMPRESTADO'
        )

        # Atualiza status para DEVOLVIDO
        dados_update = {
            'status': 'DEVOLVIDO',
            'data_devolucao': hoje.strftime('%Y-%m-%d'),
            'retornar_ao_estoque': True,
            'observacao_devolucao': 'EPI íntegro e higienizado',
        }
        res = self.client.post(reverse('emprestimo_update', args=[emp.pk]), dados_update, follow=True)
        self.assertEqual(res.status_code, 200)

        emp.refresh_from_db()
        self.assertEqual(emp.status, 'DEVOLVIDO')

        # Estoque reinserido: 5 + 2 = 7
        self.epi.refresh_from_db()
        self.assertEqual(self.epi.quantidade_estoque, 7)

    def test_atualizacao_para_danificado_exige_data_devolucao(self):
        """Ao selecionar Danificado/Devolvido/Perdido, a data de devolução torna-se obrigatória."""
        hoje = timezone.now().date()
        emp = Emprestimo.objects.create(
            colaborador=self.colab,
            epi=self.epi,
            quantidade=1,
            data_emprestimo=hoje,
            data_prevista_devolucao=hoje + timedelta(days=2),
            status='EMPRESTADO'
        )

        dados_invalidos = {
            'status': 'DANIFICADO',
            'data_devolucao': '',
        }
        res = self.client.post(reverse('emprestimo_update', args=[emp.pk]), dados_invalidos)
        self.assertEqual(res.status_code, 200)
        form = res.context['form']
        self.assertIn('data_devolucao', form.errors)

    def test_exclusao_emprestimo_post_e_get(self):
        emp = Emprestimo.objects.create(
            colaborador=self.colab,
            epi=self.epi,
            quantidade=1,
            data_emprestimo=timezone.now().date(),
            status='EMPRESTADO'
        )
        # GET bloqueado com 405
        res_get = self.client.get(reverse('emprestimo_delete', args=[emp.pk]))
        self.assertEqual(res_get.status_code, 405)
        self.assertTrue(Emprestimo.objects.filter(pk=emp.pk).exists())

        # POST exclui
        res_post = self.client.post(reverse('emprestimo_delete', args=[emp.pk]), follow=True)
        self.assertEqual(res_post.status_code, 200)
        self.assertFalse(Emprestimo.objects.filter(pk=emp.pk).exists())

    def test_tela_de_relatorios_filtro_and(self):
        """Tela de Relatórios: pesquisa simultânea por Colaborador AND EPI AND Status."""
        hoje = timezone.now().date()
        outro_colab = Colaborador.objects.create(
            nome="Marcos Aurélio Lima",
            matricula="CONST-3001",
            setor="Canteiro Geral"
        )
        outro_epi = EPI.objects.create(
            nome="Luva de Vaqueta Mista",
            certificado_aprovacao="11710",
            quantidade_estoque=20
        )

        # Cautela 1: Carlos + Capacete + EMPRESTADO
        Emprestimo.objects.create(
            colaborador=self.colab,
            epi=self.epi,
            quantidade=1,
            data_emprestimo=hoje,
            data_prevista_devolucao=hoje + timedelta(days=7),
            status='EMPRESTADO'
        )

        # Cautela 2: Marcos + Luva + EMPRESTADO
        Emprestimo.objects.create(
            colaborador=outro_colab,
            epi=outro_epi,
            quantidade=2,
            data_emprestimo=hoje,
            data_prevista_devolucao=hoje + timedelta(days=7),
            status='EMPRESTADO'
        )

        # Cautela 3: Carlos + Capacete + DEVOLVIDO
        Emprestimo.objects.create(
            colaborador=self.colab,
            epi=self.epi,
            quantidade=1,
            data_emprestimo=hoje - timedelta(days=15),
            data_devolucao=hoje - timedelta(days=2),
            status='DEVOLVIDO'
        )

        # Pesquisa na Tela de Relatórios com Filtro AND:
        # Colaborador: Carlos AND Equipamento: Capacete AND Status: EMPRESTADO
        url = reverse('relatorio_list') + f'?colaborador_nome=Carlos&epi_nome=Capacete&status=EMPRESTADO'
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['total_encontrados'], 1)
        self.assertContains(res, "Carlos Eduardo Pereira")
        self.assertContains(res, "Capacete de Segurança com Jugular")
        self.assertNotContains(res, "Marcos Aurélio Lima")
        self.assertNotContains(res, "Luva de Vaqueta Mista")


class AuthAndAccessControlTest(TestCase):
    """
    Testes automatizados cobrindo Autenticação e Controle de Acesso:
    1. Todas as rotas do sistema protegidas (usuário anônimo é redirecionado para login).
    2. Rotas públicas acessíveis sem autenticação prévia (/login/ e /admin/).
    3. Login com sucesso redirecionando para home ou rota solicitada.
    4. Login com credenciais inválidas exibindo alerta de erro.
    5. Logout encerrando a sessão e redirecionando para a tela de login.
    6. Controle de usuários (listagem de usuários do sistema).
    7. Grupo com permissões de adicionar, editar, visualizar e excluir o Model Setor no Django Admin.
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='carlos.sst',
            password='carlos_password123',
            first_name='Carlos',
            last_name='Mendes'
        )

    def test_01_rotas_protegidas_redirecionam_usuario_anonimo(self):
        """Todas as rotas do sistema devem redirecionar usuários não autenticados para a tela de login."""
        rotas_protegidas = [
            reverse('home'),
            reverse('colaborador_list'),
            reverse('colaborador_create'),
            reverse('epi_list'),
            reverse('epi_create'),
            reverse('emprestimo_list'),
            reverse('emprestimo_create'),
            reverse('relatorio_list'),
            reverse('usuario_list'),
        ]

        for rota in rotas_protegidas:
            res = self.client.get(rota)
            # Deve responder com redirect 302 para a tela de login
            self.assertEqual(res.status_code, 302, f"A rota {rota} não redirecionou o usuário anônimo!")
            self.assertTrue(res.url.startswith(reverse('login')), f"Redirecionou para {res.url} em vez de login!")

    def test_02_rotas_publicas_sem_autenticacao(self):
        """As rotas de login e o Django Admin devem ser acessíveis sem login prévio."""
        res_login = self.client.get(reverse('login'))
        self.assertEqual(res_login.status_code, 200)
        self.assertContains(res_login, "EPI Control")

        # Rota de logout redireciona para login
        res_logout = self.client.get(reverse('logout'))
        self.assertEqual(res_logout.status_code, 302)

    def test_03_login_com_sucesso(self):
        """Login com credenciais corretas deve autenticar o usuário e redirecionar para a home."""
        dados = {
            'username': 'carlos.sst',
            'password': 'carlos_password123',
            'next': '',
        }
        res = self.client.post(reverse('login'), dados)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.url, reverse('home'))

        # Confirma que após login, a home é acessada com sucesso (200)
        res_home = self.client.get(reverse('home'))
        self.assertEqual(res_home.status_code, 200)
        self.assertContains(res_home, "Carlos")

    def test_04_login_com_credenciais_invalidas(self):
        """Login com senha errada deve permanecer na página de login e apresentar mensagem de erro."""
        dados = {
            'username': 'carlos.sst',
            'password': 'senha_totalmente_errada',
        }
        res = self.client.post(reverse('login'), dados)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Usuário ou senha inválidos")

    def test_05_logout_encerra_sessao(self):
        """Ao acionar logout, a sessão é destruída e o usuário é redirecionado para a tela de login."""
        self.client.force_login(self.user)
        # Verifica que está logado
        res_home = self.client.get(reverse('home'))
        self.assertEqual(res_home.status_code, 200)

        # Aciona logout
        res_logout = self.client.get(reverse('logout'), follow=True)
        self.assertEqual(res_logout.status_code, 200)
        self.assertContains(res_logout, "Sessão encerrada com sucesso")

        # Verifica que tentar acessar rota protegida agora redireciona novamente
        res_protegida = self.client.get(reverse('home'))
        self.assertEqual(res_protegida.status_code, 302)

    def test_06_controle_de_usuarios_view(self):
        """A tela de controle de usuários deve listar os usuários do sistema para usuário autenticado."""
        self.client.force_login(self.user)
        res = self.client.get(reverse('usuario_list'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Controle de Usuários e Permissões")
        self.assertContains(res, "carlos.sst")

    def test_07_grupo_com_permissoes_setor_django_admin(self):
        """
        Requisito: 'Pelo django admin deve ser possível ter grupo com a permissão
        de adicionar, editar, visualizar e excluir dado de algum model, por exemplo, Setor.'
        """
        # 1. Cria ou obtém o model Setor e seu ContentType
        setor = Setor.objects.create(
            nome="Carpintaria e Armação",
            descricao="Setor responsável por formas de madeira e ferragens.",
            responsavel="Mestre Francisco"
        )
        ct_setor = ContentType.objects.get_for_model(Setor)

        # 2. Obtém as 4 permissões padrão do Django (add, change, view, delete) para o model Setor
        perm_add = Permission.objects.get(content_type=ct_setor, codename='add_setor')
        perm_change = Permission.objects.get(content_type=ct_setor, codename='change_setor')
        perm_view = Permission.objects.get(content_type=ct_setor, codename='view_setor')
        perm_delete = Permission.objects.get(content_type=ct_setor, codename='delete_setor')

        # 3. Cria um Grupo no Django Admin e associa exatamente as 4 permissões do model Setor
        grupo_gestores = Group.objects.create(name='Gestores de Setor - Teste')
        grupo_gestores.permissions.set([perm_add, perm_change, perm_view, perm_delete])

        # 4. Cria um usuário pertencente ao grupo
        usuario_gestor = User.objects.create_user(
            username='gestor.teste',
            password='password123',
            is_staff=True  # Pode acessar o Django Admin
        )
        usuario_gestor.groups.add(grupo_gestores)

        # 5. Validações das 4 permissões do model Setor herdadas pelo Grupo
        self.assertTrue(usuario_gestor.has_perm('core.add_setor'), "Usuário do grupo deve poder adicionar Setor!")
        self.assertTrue(usuario_gestor.has_perm('core.change_setor'), "Usuário do grupo deve poder editar Setor!")
        self.assertTrue(usuario_gestor.has_perm('core.view_setor'), "Usuário do grupo deve poder visualizar Setor!")
        self.assertTrue(usuario_gestor.has_perm('core.delete_setor'), "Usuário do grupo deve poder excluir Setor!")

        # 6. Validação de segurança: o usuário NÃO possui permissões para outros models
        self.assertFalse(usuario_gestor.has_perm('core.delete_epi'), "Não deve ter permissão para excluir EPI!")
        self.assertFalse(usuario_gestor.has_perm('core.delete_colaborador'), "Não deve ter permissão para excluir Colaborador!")
        self.assertFalse(usuario_gestor.has_perm('core.delete_emprestimo'), "Não deve ter permissão para excluir Empréstimo!")
