from django import forms
from django.utils import timezone
from .models import Colaborador, EPI, Emprestimo


class ColaboradorForm(forms.ModelForm):
    """
    Formulário para cadastro e edição de colaboradores da construtora.
    Aplica validações no servidor e estilização com classes do Bootstrap 5.
    """
    class Meta:
        model = Colaborador
        fields = ['nome', 'matricula', 'setor', 'cargo', 'email']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Raimundo Nonato dos Santos',
                'required': True,
                'autocomplete': 'off',
            }),
            'matricula': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: CONST-1050',
                'required': True,
                'autocomplete': 'off',
            }),
            'setor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Canteiro de Obras, Alvenaria, Armação, Instalações...',
                'required': True,
            }),
            'cargo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Pedreiro, Carpinteiro de Formas, Eletricista, Servente',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: raimundo.santos@construtora.com.br (opcional)',
            }),
        }
        labels = {
            'nome': 'Nome completo',
            'matricula': 'Matrícula funcional',
            'setor': 'Frente de trabalho / Setor',
            'cargo': 'Cargo / Função',
            'email': 'E-mail',
        }
        help_texts = {
            'nome': 'Campo obrigatório.',
            'matricula': 'Campo obrigatório. Deve ser única na construtora.',
            'setor': 'Campo obrigatório.',
            'cargo': 'Campo opcional.',
            'email': 'Campo opcional. Deve ser um e-mail válido.',
        }

    def clean_matricula(self):
        matricula = self.cleaned_data.get('matricula', '').strip()
        if not matricula:
            raise forms.ValidationError("A matrícula é obrigatória.")

        query = Colaborador.objects.filter(matricula__iexact=matricula)
        if self.instance and self.instance.pk:
            query = query.exclude(pk=self.instance.pk)

        if query.exists():
            raise forms.ValidationError(
                f"A matrícula '{matricula}' já está cadastrada para outro colaborador. Informe uma matrícula diferente."
            )

        return matricula

    def clean_nome(self):
        nome = self.cleaned_data.get('nome', '').strip()
        if not nome:
            raise forms.ValidationError("O nome completo é obrigatório.")
        return nome

    def clean_setor(self):
        setor = self.cleaned_data.get('setor', '').strip()
        if not setor:
            raise forms.ValidationError("O setor é obrigatório.")
        return setor


class EPIForm(forms.ModelForm):
    """
    Formulário para cadastro e edição de Equipamentos de Proteção Individual (EPIs).
    """
    class Meta:
        model = EPI
        fields = ['nome', 'descricao', 'certificado_aprovacao', 'quantidade_estoque', 'validade']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Capacete de Segurança com Jugular Aba Frontal',
                'required': True,
                'autocomplete': 'off',
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Ex: Proteção craniana contra queda de materiais e impactos em obras...',
            }),
            'certificado_aprovacao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 498 (número do C.A. do MTE)',
            }),
            'quantidade_estoque': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': '0',
                'required': True,
            }),
            'validade': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
        }
        labels = {
            'nome': 'Nome do Equipamento (EPI)',
            'descricao': 'Descrição / Finalidade',
            'certificado_aprovacao': 'Certificado de Aprovação (C.A.)',
            'quantidade_estoque': 'Quantidade em Estoque',
            'validade': 'Data de Validade (Equipamento / C.A.)',
        }
        help_texts = {
            'nome': 'Campo obrigatório. Identificação clara do EPI.',
            'descricao': 'Campo opcional. Especificações e recomendações de segurança.',
            'certificado_aprovacao': 'Número do C.A. emitido pelo Ministério do Trabalho.',
            'quantidade_estoque': 'Campo obrigatório. Saldo disponível no almoxarifado.',
            'validade': 'Campo opcional. Data de validade do equipamento ou do C.A.',
        }

    def clean_nome(self):
        nome = self.cleaned_data.get('nome', '').strip()
        if not nome:
            raise forms.ValidationError("O nome do equipamento é obrigatório.")
        return nome

    def clean_quantidade_estoque(self):
        qtd = self.cleaned_data.get('quantidade_estoque')
        if qtd is None or qtd < 0:
            raise forms.ValidationError("A quantidade em estoque não pode ser negativa.")
        return qtd


class EmprestimoCreateForm(forms.ModelForm):
    """
    Formulário para CADASTRO de novo Empréstimo de EPI.
    Requisitos da especificação:
    - Status permitidos apenas: 'Emprestado' e 'Fornecido' ('Devolvido', 'Danificado' e 'Perdido' são ocultados).
    - A data prevista para devolução deve ser posterior à data atual (quando status for Emprestado).
    - Validação de estoque disponível no almoxarifado.
    """
    STATUS_CADASTRO = [
        ('EMPRESTADO', 'Emprestado (Uso temporário que retornará ao departamento)'),
        ('FORNECIDO', 'Fornecido (Entrega permanente e definitiva ao colaborador)'),
    ]

    colaborador = forms.ModelChoiceField(
        queryset=Colaborador.objects.all().order_by('nome'),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Colaborador",
        help_text="Selecione o operário da construtora que receberá o EPI.",
        empty_label="Selecione o colaborador...",
        required=True
    )
    epi = forms.ModelChoiceField(
        queryset=EPI.objects.all().order_by('nome'),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Equipamento de Proteção Individual (EPI)",
        help_text="Selecione o equipamento a ser entregue.",
        empty_label="Selecione o equipamento...",
        required=True
    )
    quantidade = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        label="Quantidade",
        help_text="Número de unidades a retirar do almoxarifado.",
        required=True
    )
    status = forms.ChoiceField(
        choices=STATUS_CADASTRO,
        initial='EMPRESTADO',
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Tipo de Saída / Status",
        help_text="Selecione se o item é temporário (Emprestado) ou permanente (Fornecido).",
        required=True
    )

    class Meta:
        model = Emprestimo
        fields = ['colaborador', 'epi', 'quantidade', 'data_emprestimo', 'data_prevista_devolucao', 'status', 'observacoes']
        widgets = {
            'data_emprestimo': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'data_prevista_devolucao': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Ex: Fornecido para trabalho em altura na concretagem do 4º pavimento...',
            }),
        }
        labels = {
            'data_emprestimo': 'Data de Entrega do Equipamento',
            'data_prevista_devolucao': 'Data Prevista para Devolução',
            'observacoes': 'Observações Gerais',
        }
        help_texts = {
            'data_emprestimo': 'Data em que o EPI foi retirado com o técnico de SST.',
            'data_prevista_devolucao': 'Obrigatório para status Emprestado. Deve ser posterior à data atual.',
            'observacoes': 'Anotações complementares sobre a cautela.',
        }

    def clean(self):
        cleaned_data = super().clean()
        epi = cleaned_data.get('epi')
        quantidade = cleaned_data.get('quantidade')
        status = cleaned_data.get('status')
        data_prevista = cleaned_data.get('data_prevista_devolucao')
        hoje = timezone.now().date()

        # Validação de estoque suficiente
        if epi and quantidade:
            if epi.quantidade_estoque < quantidade:
                self.add_error(
                    'quantidade',
                    f"Estoque insuficiente! O EPI '{epi.nome}' possui apenas {epi.quantidade_estoque} unidade(s) disponível(is)."
                )

        # Requisito: A data prevista para devolução deve ser posterior à data e hora atuais
        if status == 'EMPRESTADO':
            if not data_prevista:
                self.add_error(
                    'data_prevista_devolucao',
                    "A data prevista para devolução é obrigatória para equipamentos com status 'Emprestado'."
                )
            elif data_prevista <= hoje:
                self.add_error(
                    'data_prevista_devolucao',
                    "A data prevista para devolução deve ser posterior à data e hora atuais (data futura)."
                )

        return cleaned_data


class EmprestimoUpdateForm(forms.ModelForm):
    """
    Formulário para ATUALIZAÇÃO / EDIÇÃO de Empréstimo de EPI.
    Requisitos da especificação:
    - Exibe todos os 5 status: 'Emprestado', 'Fornecido', 'Devolvido', 'Danificado' e 'Perdido'.
    - Impede a alteração dos campos: Colaborador, Equipamento, Data do Empréstimo e Data prevista da Devolução.
    - Permite alterar: Status, Data da Devolução e Observação na Devolução.
    - Validação: se status for Devolvido, Danificado ou Perdido, a data da devolução é obrigatória.
    """
    class Meta:
        model = Emprestimo
        fields = ['status', 'data_devolucao', 'observacao_devolucao']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_status_select',
            }),
            'data_devolucao': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'id': 'id_data_devolucao',
            }),
            'observacao_devolucao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Ex: Equipamento higienizado e apto para reuso / Devolvido com avaria na carneira...',
                'id': 'id_observacao_devolucao',
            }),
        }
        labels = {
            'status': 'Status do Equipamento',
            'data_devolucao': 'Data Efetiva da Devolução',
            'observacao_devolucao': 'Observação na Devolução',
        }
        help_texts = {
            'status': 'Atualize o estado do equipamento conforme o retorno ou extravio.',
            'data_devolucao': 'Exibido e obrigatório para os status Devolvido, Danificado ou Perdido.',
            'observacao_devolucao': 'Detalhes sobre as condições de retorno do EPI.',
        }

    retornar_ao_estoque = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'id_retornar_estoque'}),
        label="Reintegrar peças aptas ao estoque do almoxarifado?",
        help_text="Se marcado e o status for 'Devolvido', as unidades serão somadas novamente ao estoque."
    )

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        data_devolucao = cleaned_data.get('data_devolucao')

        # Se for devolvido, danificado ou perdido, data_devolucao é obrigatória
        if status in ['DEVOLVIDO', 'DANIFICADO', 'PERDIDO']:
            if not data_devolucao:
                self.add_error(
                    'data_devolucao',
                    f"Informe a data da devolução para registrar o equipamento como '{dict(Emprestimo.STATUS_CHOICES).get(status)}'."
                )

        return cleaned_data
