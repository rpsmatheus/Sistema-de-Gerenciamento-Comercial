from decimal import Decimal

from django.template import Context, Template
from django.test import SimpleTestCase

from estoque.formatos import formatar_quantidade


class FormatarQuantidadeTests(SimpleTestCase):
    def test_remove_zeros_e_usa_virgula(self):
        self.assertEqual(formatar_quantidade(Decimal('12.500')), '12,5')
        self.assertEqual(formatar_quantidade(Decimal('30.000')), '30')
        self.assertEqual(formatar_quantidade(Decimal('0.250')), '0,25')
        self.assertEqual(formatar_quantidade(Decimal('100')), '100')

    def test_filtro_de_template(self):
        template = Template('{% load estoque_tags %}{{ valor|quantidade }}')
        self.assertEqual(template.render(Context({'valor': Decimal('95.500')})), '95,5')
