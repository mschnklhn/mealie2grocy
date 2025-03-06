import logging
from typing import Tuple

from models.grocy import GrocyStockItem
from models.ingredient import Ingredient
from services.grocy_service import GrocyInstance
from services.mealie_service import MealieInstance


class UnitConverter:

    def __init__(self, grocy: GrocyInstance, mealie: MealieInstance):
        self.grocy = grocy
        self.mealie = mealie

        self.conversion_factors: dict[Tuple[str, str], float] = {}
        self.grocy_to_mealie_unit_names: dict[str, str] = {}  # To enable matching grocy unit conversions to mealie units
        self._update_conversions()

    def _update_conversions(self):
        grocy_units = self.grocy.get_units().values()
        mealie_units = self.mealie.get_units()

        self.conversion_factors: dict[Tuple[str, str], float] = {}

        # Direct mappings
        for mealie_unit in mealie_units:
            match = False

            for grocy_unit in grocy_units:
                if mealie_unit.name == grocy_unit.name:
                    match = True
                elif mealie_unit.abbreviation == grocy_unit.name:
                    match = True

                if match:
                    self.conversion_factors[(mealie_unit.name, grocy_unit.name)] = 1
                    self.grocy_to_mealie_unit_names[grocy_unit.name] = mealie_unit.name
                    break

            if not match:
                if not (mealie_unit.name in self.units_that_refer_to_any_amount
                        or mealie_unit.name in self.units_that_refer_to_one_piece):
                    raise ValueError(f"Could not find matching unit for {mealie_unit.name}")

        # Add conversions from grocy
        for conversion, factor in self.grocy.get_unit_conversions().items():
            from_unit = self.grocy_to_mealie_unit_names.get(conversion[0], conversion[0])
            to_unit = self.grocy_to_mealie_unit_names.get(conversion[1], conversion[1])

            self.conversion_factors[(from_unit, to_unit)] = factor

    units_that_refer_to_any_amount = ['Prise', 'Schuss', 'Spritzer', 'Portion', 'Scheibe', 'Esslöffel', 'Teelöffel']
    units_that_refer_to_one_piece = ['Kopf', 'Bund']

    def convert(self, source_ingredient: Ingredient, target_stock_item: GrocyStockItem) -> Ingredient:
        """
        Convert ingredient to grocy unit
        :param source_ingredient: Ingredient to convert
        :param target_stock_item: Grocy stock item to convert to
        :return: Ingredient with converted unit. Amount is 0 if any stock amount is sufficient
        """
        result_amount = 0
        result_unit = None

        if source_ingredient.unit in self.units_that_refer_to_any_amount or source_ingredient.amount == 0:
            result_amount = 0
            result_unit = target_stock_item.stock_unit

        elif source_ingredient.unit in self.units_that_refer_to_one_piece:
            result_amount = 1
            result_unit = target_stock_item.stock_unit

        elif source_ingredient.amount > 0 and source_ingredient.unit is None:
            result_amount = source_ingredient.amount
            result_unit = target_stock_item.stock_unit

        else:
            # Check if generic conversion is possible
            if (source_ingredient.unit, target_stock_item.stock_unit) in self.conversion_factors:
                result_amount = source_ingredient.amount * self.conversion_factors[(source_ingredient.unit, target_stock_item.stock_unit)]
                result_unit = target_stock_item.stock_unit

            # Check if conversion via custom stock unit is possible
            else:
                conversions = self.grocy.get_unit_conversion_resolved(target_stock_item.id)

                for (from_unit, to_unit), factor in conversions.items():
                    if from_unit in self.grocy_to_mealie_unit_names and self.grocy_to_mealie_unit_names[from_unit] == source_ingredient.unit and to_unit == target_stock_item.stock_unit:
                        result_amount = source_ingredient.amount * factor
                        result_unit = to_unit
                        break

        if result_unit is None:
            logging.error(f"Could not convert {source_ingredient.unit} to {target_stock_item.stock_unit} for product {target_stock_item.name}")
            result_amount = 1

        result_amount = round(result_amount, 2)

        return Ingredient(target_stock_item.name, result_amount, result_unit, note=source_ingredient.note, gid=target_stock_item.id, mid=source_ingredient.mid)


