import unittest

from models.grocy import GrocyProductItem, GrocyStockItem, GrocyUnit


class TestGrocyProductItem(unittest.TestCase):

    def test_from_json_with_description(self):
        data = {
            'id': 1,
            'name': 'Milk',
            'description': '<p>Fresh milk</p>'
        }
        product = GrocyProductItem.from_json(data)
        self.assertEqual(product.id, 1)
        self.assertEqual(product.name, 'Milk')
        self.assertEqual(product.description, 'Fresh milk')

    def test_from_json_without_description(self):
        data = {
            'id': 2,
            'name': 'Bread',
            'description': ''
        }
        product = GrocyProductItem.from_json(data)
        self.assertEqual(product.id, 2)
        self.assertEqual(product.name, 'Bread')
        self.assertEqual(product.description, '')

    def test_str_representation(self):
        product = GrocyProductItem(3, 'Eggs', 'Farm eggs')
        self.assertEqual(str(product), 'Eggs: Farm eggs')

class TestGrocyStockItem(unittest.TestCase):

    def test_from_json(self):
        data = {
            'product': {
                'id': 1,
                'name': 'Flour',
                'min_stock_amount': 1,
                'qu_id_stock': 1
            },
            'stock_amount_aggregated': 100,
            'quantity_unit_stock': {'name': 'kg'}
        }
        stock_item = GrocyStockItem.from_json(data)
        self.assertEqual(stock_item.id, 1)
        self.assertEqual(stock_item.name, 'Flour')
        self.assertEqual(stock_item.stock, 100)
        self.assertEqual(stock_item.min_stock, 1)
        self.assertEqual(stock_item.stock_unit_id, 1)
        self.assertEqual(stock_item.stock_unit, 'kg')

    def test_str_representation(self):
        stock_item = GrocyStockItem(1, 'Sugar', 50, 5, 2, 'kg')
        self.assertEqual(str(stock_item), '50')

class TestGrocyUnit(unittest.TestCase):

    def test_from_json(self):
        data = {
            'id': 1,
            'name': 'Liter'
        }
        unit = GrocyUnit.from_json(data)
        self.assertEqual(unit.mid, 1)
        self.assertEqual(unit.name, 'Liter')

if __name__ == '__main__':
    unittest.main()