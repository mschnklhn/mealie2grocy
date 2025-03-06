import json
import unittest
from unittest.mock import patch, MagicMock

from models.mealie import MealieFoodItem
from services.mealie_service import MealieInstance


class TestMealieInstance(unittest.TestCase):

    def setUp(self):
        self.mealie_instance = MealieInstance(api_key='dummy_key', endpoint='http://fake-api.com')

    @patch('requests.get')
    def test_get_all_foods(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = json.dumps({
            "items": [
                {"id": 1, "name": "Apple", "pluralName": "Apples", "description": "A tasty fruit", "aliases": []},
                {"id": 2, "name": "Banana", "pluralName": "Bananas", "description": "A yellow fruit", "aliases": []}
            ]
        })
        mock_get.return_value = mock_response

        foods = self.mealie_instance.get_all_foods()
        self.assertEqual(len(foods), 2)
        self.assertEqual(foods[0].name, "Apple")
        self.assertEqual(foods[1].name, "Banana")

    @patch('requests.request')
    def test_create_food_item_if_not_present(self, mock_post):
        existing_foods = [MealieFoodItem(1, "Apple", "Apples", "A tasty fruit", [])]

        mock_post.return_value.status_code = 201

        new_food = MealieFoodItem(None, "Banana", "Bananas", "A yellow fruit", [])

        self.mealie_instance.create_food_item_if_not_present(new_food, existing_foods)
        mock_post.assert_called_once()

    @patch('requests.post')
    def test_create_food_item_if_present(self, mock_post):
        existing_foods = [MealieFoodItem(1, "Apple", "Apples", "A tasty fruit", [])]

        existing_food = MealieFoodItem(None, "Apple", "Apples", "A tasty fruit", [])

        self.mealie_instance.create_food_item_if_not_present(existing_food, existing_foods)
        mock_post.assert_not_called()

    @patch('requests.get')
    def test_get_week_plan(self, mock_get):
        mock_mealplan_response = MagicMock()
        mock_mealplan_response.status_code = 200
        mock_mealplan_response.text = json.dumps({
            "items": [{"recipe": {"id": 1}}]
        })

        mock_recipe_response = MagicMock()
        mock_recipe_response.status_code = 200
        mock_recipe_response.text = json.dumps({
            "id": 1,
            "name": "Pasta",
            "recipeIngredient": [{"food": {"name": "Pasta", "id": "5"}, "quantity": 1, "unit": {"name": "kg"}}]
        })

        mock_get.side_effect = [mock_mealplan_response, mock_recipe_response]

        week_plan = self.mealie_instance.get_week_plan()
        self.assertEqual(len(week_plan), 1)
        self.assertEqual(week_plan[0].name, "Pasta")

    @patch('requests.get')
    def test_get_shopping_list_ingredients(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = json.dumps({
            "items": [
                {"food": {"name": "Apple"}, "quantity": 5, "unit": {"name": "kg"}, "note": "", "id": 1, "checked": False},
                {"food": {"name": "Banana"}, "quantity": 2, "unit": {"name": "bunches"}, "note": "", "id": 2, "checked": True}
            ]
        })
        mock_get.return_value = mock_response

        ingredients = self.mealie_instance.get_shopping_list_ingredients()
        self.assertEqual(len(ingredients), 1)
        self.assertEqual(ingredients[0].name, "Apple")
        self.assertEqual(ingredients[0].amount, 5)
        self.assertEqual(ingredients[0].unit, "kg")

    @patch('requests.get')
    @patch('requests.delete')
    def test_clear_shoppinglist(self, mock_delete, mock_get):
        mock_response_get = MagicMock()
        mock_response_get.status_code = 200
        mock_response_get.text = json.dumps({"items": [{"id": 1}, {"id": 2}]})
        mock_get.return_value = mock_response_get

        mock_response_delete = MagicMock()
        mock_response_delete.status_code = 200
        mock_delete.return_value = mock_response_delete

        self.mealie_instance.clear_shoppinglist()
        mock_get.assert_called_once()
        mock_delete.assert_called_once()

    @patch('requests.get')
    def test_test_connection_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = json.dumps({"version": "3.1.0"})
        mock_get.return_value = mock_response

        self.assertTrue(self.mealie_instance.test_connection())

    @patch('requests.get')
    def test_test_connection_failure(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        self.assertFalse(self.mealie_instance.test_connection())


if __name__ == '__main__':
    unittest.main()