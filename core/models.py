from django.db import models
from django.conf import settings
from django.utils import timezone


class Colaborador(models.Model):
    """
    Entidade Colaborador: representa os funcionários da empresa têxtil
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
        help_text="Matrícula funcional única do colaborador."
    )
    setor = models.CharField(
        max_length=100,
        verbose_name="Setor",
        help_text="Setor ou departamento onde o colaborador atua (ex: Tecelagem, Fiação, Tinturaria)."
    )
    cargo = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Cargo",
        help_text="Função ou cargo exercido (opcional)."
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
    Entidade EPI: representa os Equipamentos de Proteção Individual.
    Estrutura preparada para expansão futura do módulo de equipamentos (RF06).
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
    Entidade Empréstimo: registra a cautela/retirada e devolução de EPIs.
    Estrutura preparada para expansão futura do módulo de empréstimos (RF07 e RF09).
    """
    STATUS_CHOICES = [
        ('ATIVO', 'Ativo (Em posse do colaborador)'),
        ('DEVOLVIDO', 'Devolvido'),
        ('ATRASADO', 'Atrasado'),
    ]

    colaborador = models.ForeignKey(
        Colaborador,
        on_delete=models.PROTECT,
        related_name='emprestimos',
        verbose_name="Colaborador"
    )
    usuario_responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='emprestimos_registrados',
        verbose_name="Usuário Responsável (SST)"
    )
    data_emprestimo = models.DateField(default=timezone.now, verbose_name="Data do Empréstimo")
    data_prevista_devolucao = models.DateField(blank=True, null=True, verbose_name="Previsão de Devolução")
    data_devolucao = models.DateField(blank=True, null=True, verbose_name="Data Real da Devolução")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ATIVO',
        verbose_name="Status do Empréstimo"
    )
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    class Meta:
        verbose_name = "Empréstimo"
        verbose_name_plural = "Empréstimos"
        ordering = ['-data_emprestimo']

    def __str__(self):
        return f"Empréstimo #{self.id} - {self.colaborador.nome} ({self.get_status_display()})"


class ItemEmprestimo(models.Model):
    """
    Entidade ItemEmprestimo: relaciona os EPIs fornecidos em um determinado empréstimo.
    Permite que um mesmo empréstimo contenha múltiplos itens (relacionamento 1:N).
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
