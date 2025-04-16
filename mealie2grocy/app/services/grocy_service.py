import json
import logging
from time import sleep
from typing import Tuple

from flask_babel import _

import requests

from models.grocy import GrocyProductItem, GrocyStockItem, GrocyUnit
from models.ingredient import Ingredient


class GrocyInstance:
    def __init__(self, api_key, endpoint):
        self.api_key = api_key
        self.endpoint = endpoint
        self.default_get_headers = {
            "GROCY-API-KEY": api_key,
            "accept": "application/json"
        }

        self.default_post_headers = {
            "GROCY-API-KEY": api_key,
            "Content-Type": "application/json"
        }

    def get_all_products(self):
        url = f"{self.endpoint}/objects/products"

        retries = 3
        success = False
        while not success and retries > 0:
            # Grocy sometimes fails to respond correctly, so we retry a few times
            response = requests.get(url, headers=self.default_get_headers)

            if response.status_code != 200:
                raise Exception(f"Failed to get products from grocy: {response.text}")

            try:
                data = json.loads(response.text)
                success = True
            except json.JSONDecodeError:
                logging.error(f"Failed to decode grocy response.")
                retries -= 1
                sleep(.2)

        if not success:
            return _("Grocy does not respond. Please try again.")

        products = []
        for product in data:
            product_item = GrocyProductItem.from_json(product)

            products.append(product_item)

        return products

    def get_product(self, product_id) -> GrocyProductItem:
        url = f"{self.endpoint}/objects/products/{product_id}"

        response = requests.get(url, headers=self.default_get_headers)

        if response.status_code != 200:
            raise Exception(f"Failed to get product from grocy: {response.text}")

        data = json.loads(response.text)

        product_item = GrocyProductItem.from_json(data)

        return product_item

    def get_stock_product(self, product_id) -> GrocyStockItem:
        url = f"{self.endpoint}/stock/products/{product_id}"

        response = requests.get(url, headers=self.default_get_headers)

        if response.status_code != 200:
            raise Exception(f"Failed to get stock product from grocy: {response.text}")

        data = json.loads(response.text)
        stock_item = GrocyStockItem.from_json(data)

        return stock_item

    def get_unit(self, unit_id) -> str:
        url = f"{self.endpoint}/objects/quantity_units/{unit_id}"

        response = requests.get(url, headers=self.default_get_headers)

        if response.status_code != 200:
            raise Exception(f"Failed to get unit from grocy: {response.text}")

        data = json.loads(response.text)

        return data["name"]

    def get_shopping_list_ingredients(self) -> dict[int, 'Ingredient']:
        url = f"{self.endpoint}/objects/shopping_list"

        response = requests.get(url, headers=self.default_get_headers)

        if response.status_code != 200:
            raise Exception(f"Failed to get shopping list from grocy: {response.text}")

        data = json.loads(response.text)

        ingredients = {}
        for item in data:
            if item["done"] == 1:
                continue

            product_item = self.get_product(item["product_id"])
            unit = self.get_unit(item["qu_id"])
            gid = item["product_id"]

            if gid in ingredients:
                ingredients[gid].amount += item["amount"]
            else:
                ingredients[gid] = Ingredient(product_item.name, item["amount"], unit, gid=gid)

        return ingredients

    def get_units(self) -> dict[int, GrocyUnit]:
        url = f"{self.endpoint}/objects/quantity_units"

        response = requests.get(url, headers=self.default_get_headers)

        if response.status_code != 200:
            raise Exception(f"Failed to get units from grocy: {response.text}")

        data = json.loads(response.text)

        units = {}
        for unit_json in data:
            unit = GrocyUnit.from_json(unit_json)
            units[unit.mid] = unit

        return units

    def get_unit_conversions(self) -> dict[Tuple[str, str], float]:
        units = self.get_units()

        url = f"{self.endpoint}/objects/quantity_unit_conversions"

        response = requests.get(url, headers=self.default_get_headers)

        if response.status_code != 200:
            raise Exception(f"Failed to get conversions from grocy: {response.text}")

        data = json.loads(response.text)

        conversions = {}
        for conversion in data:
            if conversion["product_id"] is None:
                # Only include generic conversions
                from_unit = units[conversion["from_qu_id"]].name
                to_unit = units[conversion["to_qu_id"]].name
                conversions[(from_unit, to_unit)] = conversion["factor"]

        return conversions

    def get_unit_conversion_resolved(self, product_id: int) -> dict[Tuple[str, str], float]:
        url = f"{self.endpoint}/objects/quantity_unit_conversions_resolved?query%5B%5D=product_id%3D{product_id}"

        response = requests.get(url, headers=self.default_get_headers)

        if response.status_code != 200:
            raise Exception(f"Failed to get stock product from grocy: {response.text}")

        data = json.loads(response.text)

        conversions = {}
        for conversion in data:
            from_unit = conversion["from_qu_name"]
            to_unit = conversion["to_qu_name"]
            conversions[(from_unit, to_unit)] = conversion["factor"]

        return conversions

    def add_to_shopping_list(self, ingredient: 'Ingredient', amount: float):
        url = f"{self.endpoint}/objects/shopping_list"

        data = {
            "product_id": ingredient.gid,
            "amount": amount,
            "note": ingredient.note
        }

        response = requests.request("POST", url, headers=self.default_post_headers, data=json.dumps(data))

        if response.status_code != 200:
            raise Exception(f"Failed to add item to shopping list: {response.text}")

    def remove_from_shopping_list(self, gid):
        url = f"{self.endpoint}/stock/shoppinglist/remove-product"
        body = {
            "product_id": gid
        }

        response = requests.post(url, headers=self.default_post_headers, data=json.dumps(body))

        if response.status_code != 204:
            raise Exception(f"Failed to remove item from shopping list: {response.text}")

    def clear_checked_items_on_shopping_list(self):
        url = f"{self.endpoint}/stock/shoppinglist/clear"

        body = {
            "done_only": True
        }

        response = requests.post(url, headers=self.default_post_headers, data=json.dumps(body))

        if response.status_code != 204:
            raise Exception(f"Failed to clear checked items from shopping list: {response.text}")

    def add_note_to_shopping_list(self, note: str):
        url = f"{self.endpoint}/objects/shopping_lists/1"

        response = requests.get(url, headers=self.default_get_headers)

        if response.status_code != 200:
            raise Exception(f"Failed to read shopping list notes: {response.text}")

        payload = json.loads(response.text)

        current_notes = ""

        if "description" in payload:
            current_notes = payload["description"]

            if note in current_notes:
                # Do not add note if it already exists
                return

        body = {
            "description": f"{current_notes}<p>{note}</p>"
        }

        response = requests.put(url, headers=self.default_post_headers, data=json.dumps(body))

        if response.status_code != 204:
            raise Exception(f"Failed to add note to shopping list: {response.text}")

    def test_connection(self):
        url = f"{self.endpoint}/system/info"

        response = requests.get(url, headers=self.default_get_headers, timeout=1)

        if response.status_code != 200:
            return False

        return json.loads(response.text)

