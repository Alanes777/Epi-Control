from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import Colaborador, EPI, Emprestimo, ItemEmprestimo


class Command(BaseCommand):
    help = "Popula o banco de dados com registros iniciais de colaboradores, EPIs e empréstimos para a empresa têxtil."

    def handle(self, *args, **options):
        # 1. Colaboradores da Indústria Têxtil
        colaboradores_iniciais = [
            {
                'nome': 'Ana Paula da Silva',
                'matricula': 'TEX-1001',
                'setor': 'Tecelagem',
                'cargo': 'Operadora de Tear Industrial',
                'email': 'ana.silva@textilmodelo.com.br',
            },
            {
                'nome': 'Carlos Eduardo de Oliveira',
                'matricula': 'TEX-1002',
                'setor': 'Tinturaria',
                'cargo': 'Colorista Industrial',
                'email': 'carlos.oliveira@textilmodelo.com.br',
            },
            {
                'nome': 'Mariana Costa Souza',
                'matricula': 'TEX-1003',
                'setor': 'Fiação',
                'cargo': 'Auxiliar de Fiação',
                'email': 'mariana.souza@textilmodelo.com.br',
            },
            {
                'nome': 'Roberto Mendes dos Santos',
                'matricula': 'TEX-1004',
                'setor': 'Manutenção Mecânica',
                'cargo': 'Mecânico Ajustador de Teares',
                'email': 'roberto.mendes@textilmodelo.com.br',
            },
            {
                'nome': 'Fernanda Lima Ribeiro',
                'matricula': 'TEX-1005',
                'setor': 'Costura e Acabamento',
                'cargo': 'Costureira Industrial',
                'email': 'fernanda.ribeiro@textilmodelo.com.br',
            },
        ]

        colabs_dict = {}
        for dados in colaboradores_iniciais:
            colab, _ = Colaborador.objects.get_or_create(
                matricula=dados['matricula'],
                defaults=dados
            )
            colabs_dict[dados['matricula']] = colab

        # 2. EPIs da Indústria Têxtil
        epis_iniciais = [
            {
                'nome': 'Protetor Auditivo Tipo Concha (Atenuação 24dB)',
                'certificado_aprovacao': '5745',
                'quantidade_estoque': 35,
                'descricao': 'Proteção auditiva necessária devido aos ruídos constantes das máquinas de fiação e teares.'
            },
            {
                'nome': 'Respirador Semi-Facial com Filtro P2 contra Poeira de Algodão',
                'certificado_aprovacao': '4115',
                'quantidade_estoque': 50,
                'descricao': 'Proteção respiratória para evitar a inalação de partículas e fibras de algodão em suspensão.'
            },
            {
                'nome': 'Luva Nitrílica Resistente a Corantes e Solventes',
                'certificado_aprovacao': '25116',
                'quantidade_estoque': 40,
                'descricao': 'Utilizada pelos operadores e químicos do setor de tinturaria e alvejamento.'
            },
            {
                'nome': 'Óculos de Segurança com Lente Anti-Embaçante',
                'certificado_aprovacao': '15649',
                'quantidade_estoque': 60,
                'descricao': 'Proteção visual contra fragmentos de agulhas e partículas de ar comprimido.'
            },
        ]

        epis_dict = {}
        for dados in epis_iniciais:
            epi, _ = EPI.objects.get_or_create(
                nome=dados['nome'],
                defaults=dados
            )
            epis_dict[dados['nome']] = epi

        # 3. Empréstimos Iniciais (RF07 e RF09)
        hoje = timezone.now().date()

        if not Emprestimo.objects.exists():
            # Empréstimo 1: Ativo (Ana Paula - Protetor Concha)
            emp1 = Emprestimo.objects.create(
                colaborador=colabs_dict['TEX-1001'],
                data_emprestimo=hoje - timedelta(days=15),
                data_prevista_devolucao=hoje + timedelta(days=75),
                status='ATIVO',
                observacoes='Entrega de rotina para operação no galpão de tecelagem.'
            )
            ItemEmprestimo.objects.create(
                emprestimo=emp1,
                epi=epis_dict['Protetor Auditivo Tipo Concha (Atenuação 24dB)'],
                quantidade=1
            )

            # Empréstimo 2: Ativo (Carlos Eduardo - Luva Nitrílica)
            emp2 = Emprestimo.objects.create(
                colaborador=colabs_dict['TEX-1002'],
                data_emprestimo=hoje - timedelta(days=5),
                data_prevista_devolucao=hoje + timedelta(days=25),
                status='ATIVO',
                observacoes='Luva para manuseio de corantes reativos na tinturaria.'
            )
            ItemEmprestimo.objects.create(
                emprestimo=emp2,
                epi=epis_dict['Luva Nitrílica Resistente a Corantes e Solventes'],
                quantidade=2
            )

            # Empréstimo 3: Devolvido (Mariana Costa - Respirador P2)
            emp3 = Emprestimo.objects.create(
                colaborador=colabs_dict['TEX-1003'],
                data_emprestimo=hoje - timedelta(days=40),
                data_prevista_devolucao=hoje - timedelta(days=10),
                data_devolucao=hoje - timedelta(days=8),
                status='DEVOLVIDO',
                observacoes='Equipamento devolvido higienizado após conclusão da limpeza de cardas.'
            )
            ItemEmprestimo.objects.create(
                emprestimo=emp3,
                epi=epis_dict['Respirador Semi-Facial com Filtro P2 contra Poeira de Algodão'],
                quantidade=1
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Banco de dados atualizado com sucesso! "
                f"Colaboradores: {Colaborador.objects.count()} | "
                f"EPIs: {EPI.objects.count()} | "
                f"Empréstimos: {Emprestimo.objects.count()}."
            )
        )
