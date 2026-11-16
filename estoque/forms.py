from django import forms

from .formatos import formatar_quantidade
from .models import ItemEstoque, Movimentacao


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


class MovimentacaoForm(forms.ModelForm):
    """Formulário de entrada ou saída de um item.

    Recebe o item no momento da criação: MovimentacaoForm(item=item).
    A gravação é feita pela função registrar_movimentacao, em services.py.
    """

    class Meta:
        model = Movimentacao
        fields = ['tipo', 'quantidade', 'observacao']
        widgets = {
            'tipo': forms.RadioSelect,
            'quantidade': forms.NumberInput(attrs={'step': '0.001', 'min': '0.001'}),
            'observacao': forms.TextInput(attrs={
                'placeholder': 'Ex.: Compra do Moinho Serra Azul, produção da semana',
            }),
        }

    def __init__(self, *args, item, **kwargs):
        self.item = item
        super().__init__(*args, **kwargs)
        self.fields['tipo'].choices = Movimentacao.Tipo.choices
        self.fields['quantidade'].help_text = f'Em {item.get_unidade_medida_display().lower()}.'

    def clean(self):
        dados = super().clean()
        tipo = dados.get('tipo')
        quantidade = dados.get('quantidade')
        if tipo == Movimentacao.Tipo.SAIDA and quantidade and quantidade > self.item.quantidade:
            self.add_error(
                'quantidade',
                f'Estoque insuficiente: há apenas {formatar_quantidade(self.item.quantidade)} '
                f'{self.item.unidade_medida} disponíveis.',
            )
        return dados
