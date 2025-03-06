import logging

from models.ingredient import Ingredient


class MealieFoodItem:
    def __init__(self, mid, name, plural_name=None, description=None, aliases=None):
        if aliases is None:
            aliases = []
        self.mid = mid
        self.name = name
        self.plural_name = plural_name
        self.description = description
        self.aliases = aliases

    def __str__(self):
        return f"{self.name} ({self.plural_name}): {self.description}"


class MealieRecipe:
    def __init__(self, mid, name, ingredients):
        self.mid = mid
        self.name = name
        self.ingredients: list[Ingredient] = ingredients

    @classmethod
    def from_json(cls, data):
        mealie_ingredients = []
        for ingredient_json in data["recipeIngredient"]:
            mealie_ingredient = Ingredient.from_mealie_json(ingredient_json)

            if mealie_ingredient is None:
                logging.warning(f"Could not identify food item {ingredient_json['display']} in recipe {data['name']}")
                continue

            if mealie_ingredient.amount == 0:
                continue

            mealie_ingredients.append(mealie_ingredient)

        return MealieRecipe(data["id"], data["name"], mealie_ingredients)

class MealieUnit:
    def __init__(self, mid, name, abbreviation):
        self.mid = mid
        self.name = name
        self.abbreviation = abbreviation

    @classmethod
    def from_json(cls, data):
        abbreviation = data["abbreviation"]
        if len(abbreviation) == 0:
            abbreviation = None

        return cls(data["id"], data["name"], abbreviation)
