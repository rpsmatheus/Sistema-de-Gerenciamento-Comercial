from django import forms
from django.utils import timezone

from .models import Funcionario


class FuncionarioForm(forms.ModelForm):
    """Formulário de cadastro e edição de funcionários."""

    class Meta:
        model = Funcionario
        fields = ['nome', 'unidade', 'cargo', 'telefone', 'email', 'data_admissao', 'situacao']
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Nome completo'}),
            'telefone': forms.TextInput(attrs={'placeholder': '(00) 00000-0000'}),
            'email': forms.EmailInput(attrs={'placeholder': 'nome@exemplo.com'}),
            # type="date" faz o navegador mostrar um calendário.
            'data_admissao': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Texto da primeira opção das listas de seleção.
        self.fields['unidade'].empty_label = 'Selecione a unidade'
        self.fields['cargo'].choices = [('', 'Selecione o cargo')] + list(
            Funcionario.Cargo.choices
        )

    def clean_nome(self):
        return self.cleaned_data['nome'].strip()

    def clean_data_admissao(self):
        data = self.cleaned_data['data_admissao']
        if data > timezone.localdate():
            raise forms.ValidationError('A data de admissão não pode estar no futuro.')
        return data
