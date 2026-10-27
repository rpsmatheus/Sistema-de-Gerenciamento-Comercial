from django import forms

from .models import Unidade


class UnidadeForm(forms.ModelForm):
    """Formulário de cadastro e edição de unidades."""

    class Meta:
        model = Unidade
        fields = ['nome', 'endereco', 'telefone']
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Ex.: Unidade Centro'}),
            'endereco': forms.TextInput(attrs={'placeholder': 'Rua, número e bairro'}),
            'telefone': forms.TextInput(attrs={'placeholder': '(00) 0000-0000'}),
        }
        error_messages = {
            'nome': {'unique': 'Já existe uma unidade com este nome.'},
        }

    def clean_nome(self):
        # Remove espaços no início e no fim, para "Centro" e " Centro "
        # não virarem duas unidades diferentes.
        return self.cleaned_data['nome'].strip()
