from django import forms
from django.utils import timezone

from .models import Lancamento


class LancamentoForm(forms.ModelForm):
    """Formulário de cadastro e edição de lançamentos de faturamento."""

    class Meta:
        model = Lancamento
        fields = ['unidade', 'data', 'valor', 'descricao']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'valor': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01'}),
            'descricao': forms.TextInput(attrs={
                'placeholder': 'Ex.: Vendas do balcão, encomenda do Hotel Bela Vista',
            }),
        }
        help_texts = {
            'valor': 'Use ponto para os centavos, por exemplo 1250.90.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['unidade'].empty_label = 'Selecione a unidade'
        # Num lançamento novo, a data já vem preenchida com hoje.
        if not self.instance.pk:
            self.initial.setdefault('data', timezone.localdate())

    def clean_descricao(self):
        return self.cleaned_data['descricao'].strip()

    def clean_data(self):
        data = self.cleaned_data['data']
        if data > timezone.localdate():
            raise forms.ValidationError('Não é possível lançar faturamento em uma data futura.')
        return data
