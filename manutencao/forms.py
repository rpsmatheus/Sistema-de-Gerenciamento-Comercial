from django import forms
from django.utils import timezone

from .models import Equipamento, Manutencao


class EquipamentoForm(forms.ModelForm):
    """Formulário de cadastro e edição de equipamentos."""

    class Meta:
        model = Equipamento
        fields = ['nome', 'unidade', 'marca_modelo', 'data_aquisicao', 'observacoes']
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Ex.: Forno de lastro 1'}),
            'marca_modelo': forms.TextInput(attrs={'placeholder': 'Opcional'}),
            'data_aquisicao': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'observacoes': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Capacidade, garantia, cuidados de uso',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['unidade'].empty_label = 'Selecione a unidade'

    def clean_nome(self):
        return self.cleaned_data['nome'].strip()

    def clean_data_aquisicao(self):
        data = self.cleaned_data['data_aquisicao']
        if data and data > timezone.localdate():
            raise forms.ValidationError('A data de aquisição não pode estar no futuro.')
        return data


class ManutencaoForm(forms.ModelForm):
    """Formulário de registro e edição de manutenções."""

    class Meta:
        model = Manutencao
        fields = ['equipamento', 'tipo', 'data', 'descricao', 'status', 'custo', 'fornecedor']
        widgets = {
            'descricao': forms.TextInput(attrs={
                'placeholder': 'Ex.: Troca da resistência, limpeza dos queimadores',
            }),
            'data': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'custo': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }
        help_texts = {
            'data': 'Data em que a manutenção foi feita ou está agendada.',
            'custo': 'Deixe 0 se ainda não houver custo.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['equipamento'].empty_label = 'Selecione o equipamento'
        self.fields['equipamento'].queryset = Equipamento.objects.select_related('unidade')
        self.fields['fornecedor'].empty_label = 'Feita pela própria equipe'
        self.fields['tipo'].choices = [('', 'Selecione o tipo')] + list(Manutencao.Tipo.choices)

    def clean(self):
        dados = super().clean()
        # Uma manutenção pode ser agendada para o futuro, mas não pode
        # estar concluída em uma data que ainda não chegou.
        data = dados.get('data')
        if (
            dados.get('status') == Manutencao.Status.CONCLUIDA
            and data
            and data > timezone.localdate()
        ):
            self.add_error('data', 'Uma manutenção concluída não pode ter data no futuro.')
        return dados
