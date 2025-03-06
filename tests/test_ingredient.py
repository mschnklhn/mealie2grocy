import unittest

from models.ingredient import Ingredient


class TestIngredient(unittest.TestCase):

    def test_add_same_unit(self):
        ingredient1 = Ingredient(name="Sugar", amount=100, unit="g", note="for cake")
        ingredient2 = Ingredient(name="Sugar", amount=50, unit="g", note="")

        ingredient1.add(ingredient2)
        self.assertEqual(ingredient1.amount, 150)
        self.assertEqual(ingredient1.note, "for cake")

    def test_add_different_units(self):
        ingredient1 = Ingredient(name="Flour", amount=100, unit="g")
        ingredient2 = Ingredient(name="Flour", amount=1, unit="kg")

        with self.assertRaises(ValueError) as context:
            ingredient1.add(ingredient2)

        self.assertTrue("Cannot add ingredients with different units" in str(context.exception))

    def test_add_with_notes(self):
        ingredient1 = Ingredient(name="Butter", amount=100, unit="g", note="for cookies")
        ingredient2 = Ingredient(name="Butter", amount=50, unit="g", note="for cake")

        ingredient1.add(ingredient2)
        self.assertEqual(ingredient1.amount, 150)
        self.assertEqual(ingredient1.note, "for cookies, for cake")

    def test_from_mealie_json_valid(self):
        data = {
            "food": {"name": "Eggs", "id": 1},
            "quantity": 12,
            "unit": {"name": "pieces"}
        }

        ingredient = Ingredient.from_mealie_json(data)
        self.assertIsNotNone(ingredient)
        self.assertEqual(ingredient.name, "Eggs")
        self.assertEqual(ingredient.amount, 12)
        self.assertEqual(ingredient.unit, "pieces")
        self.assertEqual(ingredient.mid, 1)

    def test_from_mealie_json_no_food(self):
        data = {
            "food": None,
            "quantity": 0,
            "unit": None
        }

        ingredient = Ingredient.from_mealie_json(data)
        self.assertIsNone(ingredient)

    def test_str_representation(self):
        ingredient = Ingredient(name="Milk", amount=1, unit="L", note="fresh")
        self.assertEqual(str(ingredient), "1 L Milk (fresh)")

    def test_repr(self):
        ingredient = Ingredient(name="Milk", amount=1, unit="L", note="fresh")
        self.assertEqual(repr(ingredient), "1 L Milk (fresh)")

if __name__ == '__main__':
    unittest.main()