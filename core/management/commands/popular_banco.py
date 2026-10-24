from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import Colaborador, EPI, Emprestimo, ItemEmprestimo


class Command(BaseCommand):
    help = "Popula o banco de dados com registros realistas para a empresa de Construção Civil (EPI Control)."

    def handle(self, *args, **options):
        # 1. Colaboradores da Construção Civil
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
                'setor': 'Canteiro Geral',
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

        # 2. EPIs da Construção Civil
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

        # 3. Empréstimos Iniciais com os novos status
        hoje = timezone.now().date()

        # Limpamos empréstimos de demonstração anteriores se não forem da construtora
        Emprestimo.objects.all().delete()

        # Empréstimo 1: EMPRESTADO (Regular, no prazo)
        emp1 = Emprestimo.objects.create(
            colaborador=colabs_dict['CONST-1010'],
            epi=epis_dict['Capacete de Segurança com Jugular Aba Frontal'],
            quantidade=1,
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

        # Empréstimo 2: EMPRESTADO (Atrasado - para teste visual da sinalização de atraso)
        emp2 = Emprestimo.objects.create(
            colaborador=colabs_dict['CONST-1020'],
            epi=epis_dict['Cinto de Segurança Tipo Paraquedista com Talabarte Duplo'],
            quantidade=1,
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

        # Empréstimo 3: FORNECIDO (Entrega definitiva ao colaborador)
        emp3 = Emprestimo.objects.create(
            colaborador=colabs_dict['CONST-1030'],
            epi=epis_dict['Óculos de Proteção Ampla Visão Anti-Risco e Anti-Embaçante'],
            quantidade=1,
            data_emprestimo=hoje - timedelta(days=15),
            status='FORNECIDO',
            observacoes='Fornecimento individual definitivo para trabalho na bancada de corte de ferragens.'
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
            data_emprestimo=hoje - timedelta(days=20),
            data_prevista_devolucao=hoje - timedelta(days=5),
            data_devolucao=hoje - timedelta(days=5),
            status='DEVOLVIDO',
            observacao_devolucao='Devolvido limpo após conclusão da passagem de eletrodutos subterrâneos.'
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
            data_emprestimo=hoje - timedelta(days=8),
            data_prevista_devolucao=hoje - timedelta(days=1),
            data_devolucao=hoje - timedelta(days=1),
            status='DANIFICADO',
            observacao_devolucao='Rasgo transversal causado por atrito contra perfil metálico pontiagudo.'
        )
        ItemEmprestimo.objects.create(
            emprestimo=emp5,
            epi=epis_dict['Luva de Vaqueta Mista para Trabalho Pesado'],
            quantidade=2
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Banco de dados populado com sucesso para Construção Civil! "
                f"Colaboradores: {Colaborador.objects.count()} | "
                f"EPIs: {EPI.objects.count()} | "
                f"Empréstimos/Cautelas: {Emprestimo.objects.count()}."
            )
        )
