import unittest
from unittest.mock import patch, MagicMock

from main import test_grocy_connection, test_mealie_connection, update_products_in_mealie, compare_product_databases, \
    update_grocy_shoppinglist_from_mealie
from models.grocy import GrocyProductItem
from models.ingredient import Ingredient
from models.mealie import MealieFoodItem


class TestServiceFunctions(unittest.TestCase):


    @patch('services.grocy_service.GrocyInstance.test_connection')
    def test_test_grocy_connection(self, mock_grocy):
        mock_grocy.test_connection.return_value = {"grocy_version": {"Version": "3.1.0"}}
        self.assertTrue(test_grocy_connection())

    @patch('services.mealie_service.MealieInstance.test_connection')
    def test_test_mealie_connection(self, mock_mealie):
        mock_mealie.test_connection.return_value = {"production": True, "version": "v2.7.1"}
        self.assertTrue(test_mealie_connection())

    @patch('services.grocy_service.GrocyInstance.get_all_products')
    @patch('services.mealie_service.MealieInstance.get_all_foods')
    @patch('services.mealie_service.MealieInstance.create_food_items_from_grocy_products_if_not_present')
    def test_update_products_in_mealie(self, mock_create_mealie, mock_mealie, mock_grocy):
        mock_grocy.return_value = [MagicMock(name='Product1'), MagicMock(name='Product2')]
        mock_mealie.return_value = [MagicMock(name='Product1')]
        mock_create_mealie.return_value = None

        self.assertIs(update_products_in_mealie(), None)

    @patch('services.grocy_service.GrocyInstance.get_all_products')
    @patch('services.mealie_service.MealieInstance.get_all_foods')
    def test_compare_product_databases(self, mock_mealie, mock_grocy):
        m1, m2, m3 = MagicMock(), MagicMock(), MagicMock()
        m1.name, m2.name, m3.name = 'Product1', 'Product2', 'Product3'

        mock_grocy.return_value = [m1, m3]
        mock_mealie.return_value = [m2, m3]

        result = compare_product_databases()
        self.assertIn("Product1 missing in Mealie.", result)
        self.assertIn("Product2 missing in Grocy.", result)
        self.assertNotIn("Product3", result)

if __name__ == '__main__':
    unittest.main()