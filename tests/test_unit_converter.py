import unittest
from unittest.mock import MagicMock

from models.grocy import GrocyStockItem
from models.ingredient import Ingredient
from services.grocy_service import GrocyInstance
from services.mealie_service import MealieInstance
from services.unit_converter import UnitConverter


class TestUnitConverter(unittest.TestCase):

    def setUp(self):
        # Mock Grocy and Mealie instances
        self.mock_grocy = MagicMock(spec=GrocyInstance)
        self.mock_mealie = MagicMock(spec=MealieInstance)

        kg = MagicMock(abbreviation='kg')
        kg.name = 'Kilogram'
        g = MagicMock(abbreviation='g')
        g.name = 'Gram'

        mkg = MagicMock()
        mkg.name = 'Kilogram'
        mg = MagicMock()
        mg.name = 'Gram'

        # Mocked responses for get_units
        self.mock_grocy.get_units.return_value = {
            'kg': kg,
            'g': g
        }
        self.mock_mealie.get_units.return_value = [
            mkg,
            mg
        ]

        # Mocked response for get_unit_conversions
        self.mock_grocy.get_unit_conversions.return_value = {
            ('g', 'kg'): 0.001,
            ('kg', 'g'): 1000
        }

        # Mocked response for get_unit_conversion_resolved
        self.mock_grocy.get_unit_conversion_resolved.return_value = {
            ('g', 'kg'): 0.001
        }

        self.unit_converter = UnitConverter(self.mock_grocy, self.mock_mealie)

    def test_convert_any_amount_unit(self):
        ingredient = Ingredient("Flour", 0, "Prise", None)
        stock_item = GrocyStockItem(1, "Flour", "g", 100, 5, 'g')

        converted_ingredient = self.unit_converter.convert(ingredient, stock_item)
        self.assertEqual(converted_ingredient.amount, 0)
        self.assertEqual(converted_ingredient.unit, "g")

    def test_convert_one_piece_unit(self):
        ingredient = Ingredient("Garlic", 1, "Kopf", None)
        stock_item = GrocyStockItem(1, "Garlic", "g", 100, 5, 'g')

        converted_ingredient = self.unit_converter.convert(ingredient, stock_item)
        self.assertEqual(converted_ingredient.amount, 1)
        self.assertEqual(converted_ingredient.unit, "g")

    def test_convert_with_direct_conversion(self):
        ingredient = Ingredient("Sugar", 1000, "g", None)
        stock_item = GrocyStockItem(2, "Sugar", "kg", 1, 5, 'kg')

        converted_ingredient = self.unit_converter.convert(ingredient, stock_item)
        self.assertEqual(converted_ingredient.amount, 1)
        self.assertEqual(converted_ingredient.unit, "kg")

    def test_convert_with_custom_stock_conversion(self):
        ingredient = Ingredient("Salt", 1000, "g", None)
        stock_item = GrocyStockItem(3, "Salt", "kg", 1, 5, 'kg')

        self.mock_grocy.get_unit_conversion_resolved.return_value = {
            ('g', 'kg'): 0.001
        }

        converted_ingredient = self.unit_converter.convert(ingredient, stock_item)
        self.assertEqual(converted_ingredient.amount, 1)
        self.assertEqual(converted_ingredient.unit, 'kg')

    def test_conversion_error(self):
        ingredient = Ingredient("Pepper", 500, "g", None)
        stock_item = GrocyStockItem(4, "Pepper", "g", 1, 5, 'g')

        with self.assertLogs(level='ERROR') as log:
            converted_ingredient = self.unit_converter.convert(ingredient, stock_item)
            self.assertIn('Could not convert', log.output[0])

if __name__ == '__main__':
    unittest.main()