from django.core.management.base import BaseCommand
from core.models import Colaborador, EPI


class Command(BaseCommand):
    help = "Popula o banco de dados com registros iniciais de colaboradores e EPIs para a empresa têxtil."

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

        criados_colabs = 0
        for dados in colaboradores_iniciais:
            colab, created = Colaborador.objects.get_or_create(
                matricula=dados['matricula'],
                defaults=dados
            )
            if created:
                criados_colabs += 1

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

        criados_epis = 0
        for dados in epis_iniciais:
            epi, created = EPI.objects.get_or_create(
                nome=dados['nome'],
                defaults=dados
            )
            if created:
                criados_epis += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Banco de dados atualizado com sucesso! "
                f"Novos colaboradores: {criados_colabs} | Novos EPIs: {criados_epis}."
            )
        )
