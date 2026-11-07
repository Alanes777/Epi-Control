from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from datetime import timedelta
from core.models import Setor, Colaborador, EPI, Emprestimo, ItemEmprestimo


class Command(BaseCommand):
    help = "Popula o banco de dados com usuários, grupos de permissões (Setor), setores, colaboradores, EPIs e empréstimos da Construção Civil."

    def handle(self, *args, **options):
        # ========================================================
        # 1. MODEL SETOR, GRUPOS E PERMISSÕES (DJANGO ADMIN)
        # ========================================================
        # Criação de Setores da Construtora
        setores_iniciais = [
            {
                'nome': 'Canteiro de Obras / Alvenaria',
                'descricao': 'Execução de alvenaria estrutural e de vedação, assentamento de blocos e reboco.',
                'responsavel': 'Mestre José Carlos'
            },
            {
                'nome': 'Estruturas de Concreto',
                'descricao': 'Montagem de fôrmas, escoramento e concretagem de lajes e vigas.',
                'responsavel': 'Encarregado Valdir'
            },
            {
                'nome': 'Armação de Aço',
                'descricao': 'Corte, dobra e montagem de ferragens e armaduras para fundações e pilares.',
                'responsavel': 'Encarregada Mariana'
            },
            {
                'nome': 'Instalações Elétricas e Hidráulicas',
                'descricao': 'Passagem de eletrodutos, fiação, cabeamento e tubulações hidrossanitárias.',
                'responsavel': 'Técnico Roberto Silva'
            },
            {
                'nome': 'Canteiro Geral & Acabamento',
                'descricao': 'Logística do canteiro, limpeza de obra, revestimentos cerâmicos e pintura.',
                'responsavel': 'Encarregado Marcos'
            },
        ]

        for s_data in setores_iniciais:
            Setor.objects.update_or_create(nome=s_data['nome'], defaults=s_data)

        # Configuração de Grupo com Permissões específicas no Model Setor
        ct_setor = ContentType.objects.get_for_model(Setor)
        perms_setor = Permission.objects.filter(
            content_type=ct_setor,
            codename__in=['add_setor', 'change_setor', 'view_setor', 'delete_setor']
        )

        grupo_setor, _ = Group.objects.get_or_create(name='Gestores de Setor')
        grupo_setor.permissions.set(perms_setor)

        # Grupo Técnicos de SST (acesso operacional completo ao almoxarifado e cautelas)
        grupo_sst, _ = Group.objects.get_or_create(name='Técnicos de SST')
        ct_colab = ContentType.objects.get_for_model(Colaborador)
        ct_epi = ContentType.objects.get_for_model(EPI)
        ct_emp = ContentType.objects.get_for_model(Emprestimo)
        perms_sst = Permission.objects.filter(content_type__in=[ct_colab, ct_epi, ct_emp, ct_setor])
        grupo_sst.permissions.set(perms_sst)

        # ========================================================
        # 2. CRIAÇÃO DE USUÁRIOS DO SISTEMA
        # ========================================================
        # 1. Superadministrador
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@construtora.com.br',
                'first_name': 'Administrador',
                'last_name': 'Geral',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
            }
        )
        admin_user.set_password('admin123')
        admin_user.save()

        # 2. Usuário Gestor de Setores (demonstração de permissões no Django Admin para Setor)
        gestor_user, _ = User.objects.get_or_create(
            username='gestor.setor',
            defaults={
                'email': 'gestor.setor@construtora.com.br',
                'first_name': 'Paulo',
                'last_name': 'Gestor de Setores',
                'is_staff': True,
                'is_superuser': False,
                'is_active': True,
            }
        )
        gestor_user.set_password('gestor123')
        gestor_user.groups.set([grupo_setor])
        gestor_user.save()

        # 3. Usuário Técnico em SST (Carlos R. Mendes)
        carlos_user, _ = User.objects.get_or_create(
            username='carlos.sst',
            defaults={
                'email': 'carlos.mendes@construtora.com.br',
                'first_name': 'Carlos R.',
                'last_name': 'Mendes',
                'is_staff': True,
                'is_superuser': False,
                'is_active': True,
            }
        )
        carlos_user.set_password('carlos123')
        carlos_user.groups.set([grupo_sst])
        carlos_user.save()

        # ========================================================
        # 3. COLABORADORES DA CONSTRUÇÃO CIVIL
        # ========================================================
        colaboradores_iniciais = [
            {
                'nome': 'Raimundo Nonato dos Santos',
                'matricula': 'CONST-1010',
                'setor': 'Canteiro de Obras / Alvenaria',
                'cargo': 'Pedreiro',
                'email': 'raimundo.santos@construtora.com.br',
            },
            {
                'nome': 'Carlos Eduardo de Oliveira',
                'matricula': 'CONST-1020',
                'setor': 'Estruturas de Concreto',
                'cargo': 'Carpinteiro de Formas',
                'email': 'carlos.oliveira@construtora.com.br',
            },
            {
                'nome': 'Mariana Costa Souza',
                'matricula': 'CONST-1030',
                'setor': 'Armação de Aço',
                'cargo': 'Armadora',
                'email': 'mariana.souza@construtora.com.br',
            },
            {
                'nome': 'Roberto Mendes da Silva',
                'matricula': 'CONST-1040',
                'setor': 'Instalações Elétricas e Hidráulicas',
                'cargo': 'Eletricista Predial',
                'email': 'roberto.silva@construtora.com.br',
            },
            {
                'nome': 'Marcos Aurélio Lima',
                'matricula': 'CONST-1050',
                'setor': 'Canteiro Geral & Acabamento',
                'cargo': 'Servente de Obras',
                'email': 'marcos.lima@construtora.com.br',
            },
        ]

        colabs_dict = {}
        for dados in colaboradores_iniciais:
            colab, _ = Colaborador.objects.update_or_create(
                matricula=dados['matricula'],
                defaults=dados
            )
            colabs_dict[dados['matricula']] = colab

        # ========================================================
        # 4. EPIS DA CONSTRUÇÃO CIVIL
        # ========================================================
        epis_iniciais = [
            {
                'nome': 'Capacete de Segurança com Jugular Aba Frontal',
                'certificado_aprovacao': '498',
                'quantidade_estoque': 45,
                'descricao': 'Proteção craniana contra impactos de objetos e quedas em obras (NR-06 e NR-18).'
            },
            {
                'nome': 'Cinto de Segurança Tipo Paraquedista com Talabarte Duplo',
                'certificado_aprovacao': '36399',
                'quantidade_estoque': 18,
                'descricao': 'Equipamento essencial para trabalhos em altura acima de 2 metros com trava-quedas (NR-35).'
            },
            {
                'nome': 'Botina de Segurança com Bico de Aço e Solado Antiderrapante',
                'certificado_aprovacao': '28512',
                'quantidade_estoque': 32,
                'descricao': 'Proteção dos pés contra perfurações de pregos, queda de blocos e escorregões.'
            },
            {
                'nome': 'Óculos de Proteção Ampla Visão Anti-Risco e Anti-Embaçante',
                'certificado_aprovacao': '15649',
                'quantidade_estoque': 55,
                'descricao': 'Proteção visual contra projeção de fagulhas, poeira de cimento e estilhaços.'
            },
            {
                'nome': 'Protetor Auditivo Tipo Plug de Silicone (15dB)',
                'certificado_aprovacao': '5745',
                'quantidade_estoque': 80,
                'descricao': 'Atenuação acústica para operadores de betoneira, serras circulares e marteletes.'
            },
            {
                'nome': 'Luva de Vaqueta Mista para Trabalho Pesado',
                'certificado_aprovacao': '11710',
                'quantidade_estoque': 38,
                'descricao': 'Proteção das mãos contra abrasão e corte no manuseio de vergalhões e blocos.'
            },
        ]

        epis_dict = {}
        for dados in epis_iniciais:
            epi, _ = EPI.objects.update_or_create(
                nome=dados['nome'],
                defaults=dados
            )
            epis_dict[dados['nome']] = epi

        # ========================================================
        # 5. EMPRÉSTIMOS E CAUTELAS DE DEMONSTRAÇÃO
        # ========================================================
        hoje = timezone.now().date()
        Emprestimo.objects.all().delete()

        # Empréstimo 1: EMPRESTADO (No prazo)
        emp1 = Emprestimo.objects.create(
            colaborador=colabs_dict['CONST-1010'],
            epi=epis_dict['Capacete de Segurança com Jugular Aba Frontal'],
            quantidade=1,
            usuario_responsavel=carlos_user,
            data_emprestimo=hoje - timedelta(days=2),
            data_prevista_devolucao=hoje + timedelta(days=28),
            status='EMPRESTADO',
            observacoes='Retirada de EPI para início na alvenaria do bloco B.'
        )
        ItemEmprestimo.objects.create(
            emprestimo=emp1,
            epi=epis_dict['Capacete de Segurança com Jugular Aba Frontal'],
            quantidade=1
        )

        # Empréstimo 2: EMPRESTADO (Atrasado)
        emp2 = Emprestimo.objects.create(
            colaborador=colabs_dict['CONST-1020'],
            epi=epis_dict['Cinto de Segurança Tipo Paraquedista com Talabarte Duplo'],
            quantidade=1,
            usuario_responsavel=carlos_user,
            data_emprestimo=hoje - timedelta(days=10),
            data_prevista_devolucao=hoje - timedelta(days=2),
            status='EMPRESTADO',
            observacoes='Cautela para montagem de formas no 3º pavimento.'
        )
        ItemEmprestimo.objects.create(
            emprestimo=emp2,
            epi=epis_dict['Cinto de Segurança Tipo Paraquedista com Talabarte Duplo'],
            quantidade=1
        )

        # Empréstimo 3: FORNECIDO (Entrega definitiva)
        emp3 = Emprestimo.objects.create(
            colaborador=colabs_dict['CONST-1030'],
            epi=epis_dict['Óculos de Proteção Ampla Visão Anti-Risco e Anti-Embaçante'],
            quantidade=1,
            usuario_responsavel=carlos_user,
            data_emprestimo=hoje - timedelta(days=15),
            status='FORNECIDO',
            observacoes='Fornecimento individual definitivo para corte de ferragens.'
        )
        ItemEmprestimo.objects.create(
            emprestimo=emp3,
            epi=epis_dict['Óculos de Proteção Ampla Visão Anti-Risco e Anti-Embaçante'],
            quantidade=1
        )

        # Empréstimo 4: DEVOLVIDO (Devolução realizada com sucesso)
        emp4 = Emprestimo.objects.create(
            colaborador=colabs_dict['CONST-1040'],
            epi=epis_dict['Botina de Segurança com Bico de Aço e Solado Antiderrapante'],
            quantidade=1,
            usuario_responsavel=carlos_user,
            data_emprestimo=hoje - timedelta(days=20),
            data_prevista_devolucao=hoje - timedelta(days=5),
            data_devolucao=hoje - timedelta(days=5),
            status='DEVOLVIDO',
            observacao_devolucao='Devolvido limpo após conclusão da passagem de eletrodutos.'
        )
        ItemEmprestimo.objects.create(
            emprestimo=emp4,
            epi=epis_dict['Botina de Segurança com Bico de Aço e Solado Antiderrapante'],
            quantidade=1
        )

        # Empréstimo 5: DANIFICADO (Equipamento avariado em obra)
        emp5 = Emprestimo.objects.create(
            colaborador=colabs_dict['CONST-1050'],
            epi=epis_dict['Luva de Vaqueta Mista para Trabalho Pesado'],
            quantidade=2,
            usuario_responsavel=carlos_user,
            data_emprestimo=hoje - timedelta(days=8),
            data_prevista_devolucao=hoje - timedelta(days=1),
            data_devolucao=hoje - timedelta(days=1),
            status='DANIFICADO',
            observacao_devolucao='Rasgo transversal causado por atrito contra perfil metálico.'
        )
        ItemEmprestimo.objects.create(
            emprestimo=emp5,
            epi=epis_dict['Luva de Vaqueta Mista para Trabalho Pesado'],
            quantidade=2
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Banco de dados populado com sucesso!\n"
                f"- Usuários criados: {User.objects.count()} (admin, gestor.setor, carlos.sst)\n"
                f"- Grupos de Permissões: {Group.objects.count()} ('Gestores de Setor' com permissões no Model Setor)\n"
                f"- Setores cadastrados: {Setor.objects.count()}\n"
                f"- Colaboradores: {Colaborador.objects.count()} | EPIs: {EPI.objects.count()} | Cautelas: {Emprestimo.objects.count()}."
            )
        )
