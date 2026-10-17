from django import forms
from .models import Colaborador, EPI


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
