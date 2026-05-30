import logging

from services.grocy_service import GrocyInstance
from services.mealie_service import MealieInstance
from services.unit_converter import UnitConverter
from models.ingredient import Ingredient
from config import GROCY_API_KEY, GROCY_ENDPOINT, MEALIE_ENDPOINT, MEALIE_API_KEY

from flask_babel import _

grocy = GrocyInstance(GROCY_API_KEY, GROCY_ENDPOINT)
mealie = MealieInstance(MEALIE_API_KEY, MEALIE_ENDPOINT)


def test_grocy_connection():
    return grocy.test_connection()


def test_mealie_connection():
    return mealie.test_connection()


def update_products_in_mealie():
    grocy_products = grocy.get_all_products()
    mealie_foods = mealie.get_all_foods()

    mealie.create_food_items_from_grocy_products_if_not_present(grocy_products, mealie_foods)


def _sync_item(kind, name, unit, need=None, stock=None, min_stock=None, on_list=None, added=None):
    return {
        "kind": kind,
        "name": name,
        "unit": unit,
        "need": need,
        "stock": stock,
        "min": min_stock,
        "list": on_list,
        "added": added,
    }


def update_grocy_shoppinglist_from_mealie():
    items = []

    grocy_products = grocy.get_all_products()

    grocy.clear_checked_items_on_shopping_list()

    converter = UnitConverter(grocy, mealie)

    # 1. Get shopping list ingredients
    ingredients = mealie.get_shopping_list_ingredients()

    # 2. Match ingredients with grocy products
    for ingredient in ingredients:
        for product in grocy_products:
            if ingredient.name == product.name:
                ingredient.gid = product.id
                break

        if ingredient.gid is None:
            logging.warning(f"Could not find product for ingredient: {ingredient.name}")
            ingredient_name = ingredient.name
            note_need = round(ingredient.amount, 2) if ingredient.amount > 0 else None
            note_added = round(ingredient.amount, 2) if ingredient.amount > 0 else 0
            if not ingredient.amount > 0:
                ingredient.amount = 0
            if ingredient.unit:
                ingredient_name += f" ({ingredient.unit})"

            grocy.add_product_note_to_shopping_list(ingredient_name, ingredient.amount)
            items.append(_sync_item(
                "note",
                ingredient.name,
                ingredient.unit or "",
                need=note_need,
                added=note_added,
            ))

    # 4. Get existing grocy shopping list
    ingredients_already_on_shopping_list = grocy.get_shopping_list_ingredients()

    # 5. Per ingredient
    converted_ingredients = []
    stock_items = {}
    for ingredient in ingredients:
        if ingredient.gid is None:
            continue

        # 5.0. Convert mealie units to grocy units if needed
        stock_item = grocy.get_stock_product(ingredient.gid)
        stock_items[ingredient.gid] = stock_item

        # Ignore opened items
        stock_item.stock -= stock_item.stock_opened

        if stock_item.stock_unit != ingredient.unit:
            logging.info(f"Converting {ingredient.unit} to {stock_item.stock_unit}")
            converted_ingredients.append(converter.convert(ingredient, stock_item))
        else:
            converted_ingredients.append(ingredient)

    # Aggregate ingredients
    to_remove = []
    for i in range(len(converted_ingredients)):
        for j in range(i + 1, len(converted_ingredients)):
            ingredient1: Ingredient = converted_ingredients[i]
            ingredient2: Ingredient = converted_ingredients[j]
            if ingredient1.gid == ingredient2.gid and ingredient1.unit == ingredient2.unit:
                ingredient1.add(ingredient2)
                to_remove.append(j)

    for i in sorted(to_remove, reverse=True):
        converted_ingredients.pop(i)

    for ingredient in converted_ingredients:
        stock_item = stock_items[ingredient.gid]

        on_shoppinglist = ingredients_already_on_shopping_list.get(ingredient.gid)
        amount_already_on_shoppinglist = on_shoppinglist.amount if on_shoppinglist else 0

        amount_needed = 0
        if ingredient.amount > 0:
            amount_needed = round(max(ingredient.amount - stock_item.stock + stock_item.min_stock - amount_already_on_shoppinglist, 0), 2)
        elif stock_item.stock == 0:
            # Any amount is sufficient
            amount_needed = round(max(1 - amount_already_on_shoppinglist, 0), 2)

        unit = stock_item.stock_unit or ingredient.unit or ""
        need = round(ingredient.amount, 2) if ingredient.amount > 0 else None

        if amount_needed > 0.05 or (amount_needed > 0 and ingredient.amount == 0):
            amount_on_list = amount_needed
            if amount_already_on_shoppinglist > 0:
                amount_on_list = round(amount_needed + amount_already_on_shoppinglist, 2)

            logging.info(
                f"Adding {amount_on_list} {ingredient.name} to shopping list "
                f"(required: {ingredient.amount}, stock: {stock_item.stock}, "
                f"min stock: {stock_item.min_stock}, already on shopping list: "
                f"{amount_already_on_shoppinglist})"
            )
            items.append(_sync_item(
                "added",
                ingredient.name,
                unit,
                need=need,
                stock=round(stock_item.stock, 2),
                min_stock=round(stock_item.min_stock, 2),
                on_list=round(amount_already_on_shoppinglist, 2),
                added=round(amount_on_list, 2),
            ))

            if amount_already_on_shoppinglist > 0:
                grocy.remove_from_shopping_list(ingredient.gid)
                amount_needed = amount_on_list

            grocy.add_to_shopping_list(ingredient, amount_needed)
        else:
            logging.info(
                f"Stock is sufficient for {ingredient.name} "
                f"(required: {ingredient.amount}, stock: {stock_item.stock}, "
                f"min stock: {stock_item.min_stock}, already on shopping list: "
                f"{amount_already_on_shoppinglist})"
            )
            items.append(_sync_item(
                "covered",
                ingredient.name,
                unit,
                need=need,
                stock=round(stock_item.stock, 2),
                min_stock=round(stock_item.min_stock, 2),
                on_list=round(amount_already_on_shoppinglist, 2),
            ))

    # mealie.clear_shoppinglist()

    return {
        "up_to_date": len(items) == 0,
        "items": items,
    }


def clear_mealie_shoppinglist():
    return mealie.clear_shoppinglist()


def compare_product_databases():
    grocy_products = grocy.get_all_products()
    mealie_foods = mealie.get_all_foods()

    result = ""
    for product in grocy_products:
        if product.name not in [food.name for food in mealie_foods]:
            result += f"{product.name} {_("missing in")} Mealie.\n"

    for food in mealie_foods:
        if food.name not in [product.name for product in grocy_products]:
            result += f"{food.name} {_("missing in")} Grocy.\n"

    if result == "":
        result = _("Product databases are identical.")

    return result
