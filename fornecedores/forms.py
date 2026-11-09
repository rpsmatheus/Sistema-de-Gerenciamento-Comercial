import re

from django import forms

from .models import Fornecedor


class FornecedorForm(forms.ModelForm):
    """Formulário de cadastro e edição de fornecedores."""

    # O campo é redefinido aqui para aceitar o CNPJ digitado com
    # pontuação (até 18 caracteres). A limpeza acontece em clean_cnpj.
    cnpj = forms.CharField(
        label='CNPJ',
        max_length=18,
        help_text='Pode digitar com ou sem pontuação.',
        widget=forms.TextInput(attrs={'placeholder': '00.000.000/0000-00'}),
        error_messages={'unique': 'Já existe um fornecedor com este CNPJ.'},
    )

    class Meta:
        model = Fornecedor
        fields = [
            'razao_social', 'nome_fantasia', 'cnpj', 'contato',
            'telefone', 'email', 'observacoes',
        ]
        widgets = {
            'razao_social': forms.TextInput(attrs={'placeholder': 'Nome registrado da empresa'}),
            'nome_fantasia': forms.TextInput(attrs={'placeholder': 'Nome comercial, se houver'}),
            'contato': forms.TextInput(attrs={'placeholder': 'Nome de quem atende a padaria'}),
            'telefone': forms.TextInput(attrs={'placeholder': '(00) 0000-0000'}),
            'email': forms.EmailInput(attrs={'placeholder': 'vendas@exemplo.com'}),
            'observacoes': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Produtos fornecidos, prazos de entrega, condições de pagamento',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Na edição, mostra o CNPJ já com pontuação.
        if self.instance.pk:
            self.initial['cnpj'] = self.instance.cnpj_formatado

    def clean_razao_social(self):
        return self.cleaned_data['razao_social'].strip()

    def clean_cnpj(self):
        # Mantém apenas os números: "12.345.678/0001-90" vira "12345678000190".
        cnpj = re.sub(r'\D', '', self.cleaned_data['cnpj'])
        if len(cnpj) != 14:
            raise forms.ValidationError('Informe um CNPJ com 14 dígitos.')
        return cnpj
