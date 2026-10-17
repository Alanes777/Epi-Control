from django import forms
from .models import Colaborador


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
        """
        Valida se a matrícula informada já está cadastrada para outro colaborador.
        Permite manter a mesma matrícula caso seja a edição do próprio registro.
        """
        matricula = self.cleaned_data.get('matricula', '').strip()
        if not matricula:
            raise forms.ValidationError("A matrícula é obrigatória.")

        # Busca por outros colaboradores com a mesma matrícula
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
