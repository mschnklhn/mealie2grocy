import unittest
from unittest.mock import patch, MagicMock
from models.ingredient import Ingredient
from models.mealie import MealieFoodItem, MealieRecipe, MealieUnit


class TestMealieFoodItem(unittest.TestCase):

    def test_initialization(self):
        food_item = MealieFoodItem(mid=1, name="Apple", plural_name="Apples", description="A tasty fruit", aliases=["Fruit"])
        self.assertEqual(food_item.mid, 1)
        self.assertEqual(food_item.name, "Apple")
        self.assertEqual(food_item.plural_name, "Apples")
        self.assertEqual(food_item.description, "A tasty fruit")
        self.assertEqual(food_item.aliases, ["Fruit"])

    def test_str_representation(self):
        food_item = MealieFoodItem(mid=1, name="Apple", plural_name="Apples", description="A tasty fruit")
        self.assertEqual(str(food_item), "Apple (Apples): A tasty fruit")

class TestMealieRecipe(unittest.TestCase):

    @patch('models.ingredient.Ingredient.from_mealie_json')
    def test_from_json(self, mock_from_mealie_json):
        # Mock the Ingredient class method
        mock_ingredient = MagicMock(spec=Ingredient)
        mock_ingredient.amount = 1
        mock_from_mealie_json.return_value = mock_ingredient

        data = {
            "id": 1,
            "name": "Apple Pie",
            "recipeIngredient": [{"display": "2 cups of flour"}, {"display": "1 cup of sugar"}]
        }

        recipe = MealieRecipe.from_json(data)
        self.assertEqual(recipe.mid, 1)
        self.assertEqual(recipe.name, "Apple Pie")
        self.assertEqual(len(recipe.ingredients), 2)

    @patch('models.ingredient.Ingredient.from_mealie_json')
    def test_from_json_with_unidentified_food_item(self, mock_from_mealie_json):
        # Mock the Ingredient class method to return None for the first ingredient
        mock_from_mealie_json.side_effect = [None, MagicMock(spec=Ingredient, amount=1)]

        data = {
            "id": 1,
            "name": "Apple Pie",
            "recipeIngredient": [{"display": "unknown ingredient"}, {"display": "1 cup of sugar"}]
        }

        with self.assertLogs(level='WARNING') as log:
            recipe = MealieRecipe.from_json(data)
            self.assertIn("Could not identify food item unknown ingredient", log.output[0])
            self.assertEqual(len(recipe.ingredients), 1)

class TestMealieUnit(unittest.TestCase):

    def test_from_json(self):
        data = {
            "id": 1,
            "name": "Liter",
            "abbreviation": "L"
        }
        unit = MealieUnit.from_json(data)
        self.assertEqual(unit.mid, 1)
        self.assertEqual(unit.name, "Liter")
        self.assertEqual(unit.abbreviation, "L")

    def test_from_json_with_empty_abbreviation(self):
        data = {
            "id": 2,
            "name": "Piece",
            "abbreviation": ""
        }
        unit = MealieUnit.from_json(data)
        self.assertEqual(unit.mid, 2)
        self.assertEqual(unit.name, "Piece")
        self.assertIsNone(unit.abbreviation)

if __name__ == '__main__':
    unittest.main()