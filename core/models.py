from django.db import models
from django.conf import settings
from django.utils import timezone


class Colaborador(models.Model):
    """
    Entidade Colaborador: representa os operários e funcionários da empresa de construção civil
    que utilizam Equipamentos de Proteção Individual (EPIs).
    """
    nome = models.CharField(
        max_length=150,
        verbose_name="Nome Completo",
        help_text="Informe o nome completo do colaborador."
    )
    matricula = models.CharField(
        max_length=30,
        unique=True,
        verbose_name="Matrícula",
        help_text="Matrícula funcional única do colaborador na construtora."
    )
    setor = models.CharField(
        max_length=100,
        verbose_name="Setor",
        help_text="Frente de trabalho ou setor (ex: Canteiro de Obras, Alvenaria, Armação, Instalações, Acabamento)."
    )
    cargo = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Cargo",
        help_text="Função exercida (ex: Pedreiro, Carpinteiro, Armador, Eletricista, Servente)."
    )
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name="E-mail",
        help_text="Endereço de e-mail institucional ou pessoal (opcional)."
    )
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Cadastrado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Colaborador"
        verbose_name_plural = "Colaboradores"
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} (Matrícula: {self.matricula})"


class EPI(models.Model):
    """
    Entidade EPI: representa os Equipamentos de Proteção Individual da construtora.
    """
    nome = models.CharField(max_length=150, verbose_name="Nome do Equipamento")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    certificado_aprovacao = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Certificado de Aprovação (CA)",
        help_text="Número do C.A. emitido pelo Ministério do Trabalho."
    )
    quantidade_estoque = models.IntegerField(default=0, verbose_name="Quantidade em Estoque")
    validade = models.DateField(blank=True, null=True, verbose_name="Validade do Equipamento / C.A.")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "EPI"
        verbose_name_plural = "EPIs"
        ordering = ['nome']

    def __str__(self):
        ca = f" - CA: {self.certificado_aprovacao}" if self.certificado_aprovacao else ""
        return f"{self.nome}{ca}"


class Emprestimo(models.Model):
    """
    Entidade Empréstimo: controla a cautela, entrega definitiva e devolução de EPIs.
    Status conforme especificação:
    - Emprestado: entrega temporária para devolução posterior.
    - Fornecido: entrega definitiva permanente (não precisará devolver, ex: uniformes).
    - Devolvido: colaborador já retornou o EPI.
    - Danificado: retornado com defeitos ou danos, passará por manutenção.
    - Perdido: colaborador não consegue devolver por motivo de extravio.
    """
    STATUS_CHOICES = [
        ('EMPRESTADO', 'Emprestado'),
        ('FORNECIDO', 'Fornecido'),
        ('DEVOLVIDO', 'Devolvido'),
        ('DANIFICADO', 'Danificado'),
        ('PERDIDO', 'Perdido'),
    ]

    colaborador = models.ForeignKey(
        Colaborador,
        on_delete=models.PROTECT,
        related_name='emprestimos',
        verbose_name="Colaborador"
    )
    epi = models.ForeignKey(
        EPI,
        on_delete=models.PROTECT,
        related_name='emprestimos',
        verbose_name="Equipamento (EPI)",
        null=True,
        blank=True
    )
    quantidade = models.PositiveIntegerField(
        default=1,
        verbose_name="Quantidade"
    )
    usuario_responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='emprestimos_registrados',
        verbose_name="Usuário Responsável (SST)"
    )
    data_emprestimo = models.DateField(
        default=timezone.now,
        verbose_name="Data de Entrega do Equipamento"
    )
    data_prevista_devolucao = models.DateField(
        blank=True,
        null=True,
        verbose_name="Data Prevista para Devolução"
    )
    data_devolucao = models.DateField(
        blank=True,
        null=True,
        verbose_name="Data Efetiva da Devolução"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='EMPRESTADO',
        verbose_name="Status do Equipamento"
    )
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações Gerais"
    )
    observacao_devolucao = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observação na Devolução"
    )
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Controle de EPI / Empréstimo"
        verbose_name_plural = "Controles de EPIs / Empréstimos"
        ordering = ['-data_emprestimo', '-id']

    def __str__(self):
        nome_epi = self.epi.nome if self.epi else "EPI"
        return f"Controle #{self.id} - {self.colaborador.nome} | {nome_epi} ({self.get_status_display()})"


class ItemEmprestimo(models.Model):
    """
    Entidade ItemEmprestimo: relacionamento de itens vinculados para compatibilidade com cautelas compostas.
    """
    emprestimo = models.ForeignKey(
        Emprestimo,
        on_delete=models.CASCADE,
        related_name='itens',
        verbose_name="Empréstimo"
    )
    epi = models.ForeignKey(
        EPI,
        on_delete=models.PROTECT,
        related_name='itens_emprestados',
        verbose_name="Equipamento (EPI)"
    )
    quantidade = models.PositiveIntegerField(default=1, verbose_name="Quantidade")

    class Meta:
        verbose_name = "Item do Empréstimo"
        verbose_name_plural = "Itens do Empréstimo"

    def __str__(self):
        return f"{self.quantidade}x {self.epi.nome} (Empréstimo #{self.emprestimo.id})"
