import re

from django import forms

from .models import Cliente


class ClienteForm(forms.ModelForm):
    """Formulário de cadastro e edição de clientes."""

    # O campo é redefinido aqui para aceitar o documento digitado com
    # pontuação (até 18 caracteres). A limpeza acontece em clean_documento.
    documento = forms.CharField(
        label='CPF ou CNPJ',
        max_length=18,
        help_text='Pode digitar com ou sem pontuação.',
        widget=forms.TextInput(attrs={'placeholder': '000.000.000-00'}),
        error_messages={'unique': 'Já existe um cliente com este CPF ou CNPJ.'},
    )

    class Meta:
        model = Cliente
        fields = ['nome', 'documento', 'telefone', 'email', 'endereco']
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Nome ou razão social'}),
            'telefone': forms.TextInput(attrs={'placeholder': '(00) 00000-0000'}),
            'email': forms.EmailInput(attrs={'placeholder': 'contato@exemplo.com'}),
            'endereco': forms.TextInput(attrs={'placeholder': 'Rua, número e bairro'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Na edição, mostra o documento já com pontuação.
        if self.instance.pk:
            self.initial['documento'] = self.instance.documento_formatado

    def clean_nome(self):
        return self.cleaned_data['nome'].strip()

    def clean_documento(self):
        # Mantém apenas os números: "123.456.789-01" vira "12345678901".
        documento = re.sub(r'\D', '', self.cleaned_data['documento'])
        if len(documento) not in (11, 14):
            raise forms.ValidationError(
                'Informe um CPF com 11 dígitos ou um CNPJ com 14 dígitos.'
            )
        return documento
