from django import forms

from .models import ItemEstoque


class ItemEstoqueForm(forms.ModelForm):
    """Formulário de cadastro e edição de itens de estoque.

    A quantidade em estoque não aparece aqui: ela só muda por meio de
    entradas e saídas.
    """

    class Meta:
        model = ItemEstoque
        fields = ['nome', 'tipo', 'unidade_medida', 'unidade', 'fornecedor', 'quantidade_minima']
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Ex.: Farinha de trigo'}),
            'quantidade_minima': forms.NumberInput(attrs={'step': '0.001', 'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['unidade'].empty_label = 'Selecione a unidade'
        self.fields['fornecedor'].empty_label = 'Sem fornecedor'
        self.fields['tipo'].choices = [('', 'Selecione o tipo')] + list(ItemEstoque.Tipo.choices)
        self.fields['unidade_medida'].choices = [('', 'Selecione a unidade de medida')] + list(
            ItemEstoque.UnidadeMedida.choices
        )

    def clean_nome(self):
        return self.cleaned_data['nome'].strip()
