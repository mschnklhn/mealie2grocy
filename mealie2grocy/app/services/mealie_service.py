import json
import logging
from datetime import datetime

import requests

from models.grocy import GrocyProductItem
from models.ingredient import Ingredient
from models.mealie import MealieFoodItem, MealieRecipe, MealieUnit


class MealieInstance:
    def __init__(self, api_key, endpoint):
        self.api_key = api_key
        self.endpoint = endpoint
        self.default_headers = {
            "Authorization": f"Bearer {api_key}",
            "accept": "application/json"
        }

    def get_all_foods(self):
        # See https://my.smada.homes:9090/group/data/foods/
        url = f"{self.endpoint}/foods?page=1&perPage=1000"

        response = requests.get(url, headers=self.default_headers)

        if response.status_code != 200:
            raise Exception(f"Failed to get foods from mealie: {response.text}")

        data = json.loads(response.text)

        # Create a list of MealieFoodItem objects
        foods = []
        for item in data["items"]:
            foods.append(MealieFoodItem(item["id"], item["name"], item["pluralName"], item["description"], item["aliases"]))

        return foods

    def create_food_items_from_grocy_products_if_not_present(self, grocy_products: list[GrocyProductItem], existing_foods: list[MealieFoodItem]):
        for product in grocy_products:
            food_item = MealieFoodItem(None, product.name, None, product.description)
            self.create_food_item_if_not_present(food_item, existing_foods)

    def create_food_item_if_not_present(self, food_item: MealieFoodItem, existing_foods: list[MealieFoodItem]):
        if food_item.name in [food.name for food in existing_foods]:
            logging.info(f"Skipping existing item: {food_item.name}")
            return

        url = f"{self.endpoint}/foods"
        data = {
            "name": food_item.name,
            "pluralName": food_item.plural_name,
            "description": food_item.description if food_item.description else "",
            "aliases": food_item.aliases
        }
        response = requests.request("POST", url, headers=self.default_headers, data=json.dumps(data))

        if response.status_code != 201:
            raise Exception(f"Failed to create food item in mealie: {response.text}")

    def get_week_plan(self) -> list[MealieRecipe]:
        url = f"{self.endpoint}/households/mealplans?start_date={datetime.now().strftime('%Y-%m-%d')}&orderBy=date&orderDirection=asc&page=1&perPage=100"

        response = requests.get(url, headers=self.default_headers)

        if response.status_code != 200:
            raise Exception(f"Failed to get week plan from mealie: {response.text}")

        data = json.loads(response.text)

        # Create a list of MealieRecipes objects
        meals = []
        for item in data["items"]:
            recipe = self.get_recipe(item["recipe"]["id"])
            meals.append(recipe)

        return meals

    def get_shopping_list_ingredients(self) -> list['Ingredient']:
        url = f"{self.endpoint}/households/shopping/items?page=1&perPage=1000"

        response = requests.get(url, headers=self.default_headers)

        if response.status_code != 200:
            raise Exception(f"Failed to get shopping list from mealie: {response.text}")

        data = json.loads(response.text)

        # Create a list of Ingredient objects
        ingredients: list[Ingredient] = []
        for food_item in data["items"]:
            if food_item["checked"] is True:
                continue

            unit = food_item["unit"]["name"] if food_item["unit"] is not None else None

            ingredient = Ingredient(food_item["food"]["name"], food_item["quantity"], unit, note=food_item["note"], mid=food_item["id"])

            ingredients.append(ingredient)

        return ingredients

    def get_recipe(self, mid) -> MealieRecipe:
        url = f"{self.endpoint}/recipes/{mid}"

        response = requests.get(url, headers=self.default_headers)

        if response.status_code != 200:
            raise Exception(f"Failed to get recipe from mealie: {response.text}")

        data = json.loads(response.text)

        return MealieRecipe.from_json(data)

    def get_units(self) -> list[MealieUnit]:
        url = f"{self.endpoint}/units?page=1&perPage=1000"

        response = requests.get(url, headers=self.default_headers)

        if response.status_code != 200:
            raise Exception(f"Failed to get units from mealie: {response.text}")

        data = json.loads(response.text)

        units = []
        for unit in data["items"]:
            units.append(MealieUnit.from_json(unit))

        return units

    def clear_shoppinglist(self):
        # Get all
        url = f"{self.endpoint}/households/shopping/items?page=1&perPage=1000"
        response = requests.get(url, headers=self.default_headers)
        items = json.loads(response.text)["items"]
        item_ids = [item["id"] for item in items]

        url = f"{self.endpoint}/households/shopping/items"
        response = requests.delete(url, headers=self.default_headers, params={"ids": item_ids})

        if response.status_code == 200:
            return True
        else:
            return False

    def test_connection(self):
        url = f"{self.endpoint}/app/about"
        response = requests.get(url)

        if response.status_code != 200:
            return False

        return json.loads(response.text)
