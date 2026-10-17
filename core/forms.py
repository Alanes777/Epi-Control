from django import forms
from django.utils import timezone
from .models import Colaborador, EPI, Emprestimo, ItemEmprestimo


class ColaboradorForm(forms.ModelForm):
    """
    Formulário para cadastro e edição de colaboradores.
    Aplica validações no servidor e estilização com classes do Bootstrap 5.
    """
    class Meta:
        model = Colaborador
        fields = ['nome', 'matricula', 'setor', 'cargo', 'email']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Maria Aparecida Santos',
                'required': True,
                'autocomplete': 'off',
            }),
            'matricula': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: TEX-1045',
                'required': True,
                'autocomplete': 'off',
            }),
            'setor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Tecelagem, Fiação, Tinturaria, Costura...',
                'required': True,
            }),
            'cargo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Operador de Tear, Tecelão, Mecânico (opcional)',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: maria.santos@empresa.com.br (opcional)',
            }),
        }
        labels = {
            'nome': 'Nome completo',
            'matricula': 'Matrícula',
            'setor': 'Setor',
            'cargo': 'Cargo',
            'email': 'E-mail',
        }
        help_texts = {
            'nome': 'Campo obrigatório.',
            'matricula': 'Campo obrigatório. Deve ser única na empresa.',
            'setor': 'Campo obrigatório. Setor fabril ou administrativo.',
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
    Formulário para cadastro e edição de Equipamentos de Proteção Individual (RF06).
    """
    class Meta:
        model = EPI
        fields = ['nome', 'descricao', 'certificado_aprovacao', 'quantidade_estoque', 'validade']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Protetor Auditivo Tipo Concha',
                'required': True,
                'autocomplete': 'off',
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Ex: Proteção do sistema auditivo contra ruídos industriais intensos no setor de teares...',
            }),
            'certificado_aprovacao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 5745 (opcional)',
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
            'nome': 'Nome do Equipamento',
            'descricao': 'Descrição / Finalidade',
            'certificado_aprovacao': 'Certificado de Aprovação (C.A.)',
            'quantidade_estoque': 'Quantidade em Estoque',
            'validade': 'Data de Validade (Equipamento / C.A.)',
        }
        help_texts = {
            'nome': 'Campo obrigatório. Identificação do EPI.',
            'descricao': 'Campo opcional. Instruções ou detalhamento técnico.',
            'certificado_aprovacao': 'Campo opcional. Número do C.A. emitido pelo Ministério do Trabalho.',
            'quantidade_estoque': 'Campo obrigatório. Quantidade física disponível no almoxarifado.',
            'validade': 'Campo opcional. Data de expiração do lote ou do C.A.',
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


class EmprestimoForm(forms.ModelForm):
    """
    Formulário para registro de novo Empréstimo / Cautela de EPI (RF07 e RF09).
    Permite selecionar o colaborador, o equipamento desejado e a quantidade,
    validando a disponibilidade imediata em estoque.
    """
    colaborador = forms.ModelChoiceField(
        queryset=Colaborador.objects.all().order_by('nome'),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Colaborador",
        help_text="Selecione o colaborador que receberá o EPI.",
        empty_label="Selecione o colaborador...",
        required=True
    )
    epi = forms.ModelChoiceField(
        queryset=EPI.objects.all().order_by('nome'),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Equipamento de Proteção (EPI)",
        help_text="Selecione o EPI a ser emprestado.",
        empty_label="Selecione o equipamento...",
        required=True
    )
    quantidade = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        label="Quantidade",
        help_text="Quantidade de peças a fornecer ao colaborador.",
        required=True
    )

    class Meta:
        model = Emprestimo
        fields = ['colaborador', 'data_emprestimo', 'data_prevista_devolucao', 'observacoes']
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
                'placeholder': 'Ex: EPI fornecido para substituição de peça danificada no turno da noite...',
            }),
        }
        labels = {
            'data_emprestimo': 'Data do Empréstimo',
            'data_prevista_devolucao': 'Previsão de Devolução (opcional)',
            'observacoes': 'Observações Adicionais',
        }
        help_texts = {
            'data_emprestimo': 'Data em que o EPI foi retirado no departamento.',
            'data_prevista_devolucao': 'Data limite prevista para a troca ou devolução do item.',
            'observacoes': 'Campo opcional para anotações do almoxarifado.',
        }

    def clean(self):
        cleaned_data = super().clean()
        epi = cleaned_data.get('epi')
        quantidade = cleaned_data.get('quantidade')

        if epi and quantidade:
            if epi.quantidade_estoque < quantidade:
                self.add_error(
                    'quantidade',
                    f"Estoque insuficiente! O EPI '{epi.nome}' possui apenas {epi.quantidade_estoque} unidade(s) disponível(is) no momento."
                )

        return cleaned_data


class DevolucaoForm(forms.Form):
    """
    Formulário para registro da devolução de um EPI emprestado.
    """
    data_devolucao = forms.DateField(
        initial=timezone.now,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="Data Efetiva da Devolução",
        help_text="Data em que o colaborador entregou o EPI no departamento de SST.",
        required=True
    )
    retornar_ao_estoque = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Reintegrar peças ao estoque do almoxarifado?",
        help_text="Marque caso os equipamentos devolvidos estejam higienizados e em perfeitas condições para reuso."
    )
    observacoes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Ex: Equipamento recebido limpo / Descarte por desgaste natural de uso...',
        }),
        label="Observações da Devolução",
        required=False
    )
