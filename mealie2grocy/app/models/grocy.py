import re


class GrocyProductItem:
    def __init__(self, gid, name, description=None):
        self.id = gid
        self.name = name
        self.description = description

    def __str__(self):
        return f"{self.name}: {self.description}"

    @classmethod
    def from_json(cls, data):
        _description = data['description']
        if _description:
            _description = re.sub('<.*?>', '', _description).strip()
            if len(_description) <= 1:
                _description = None

        return cls(data['id'], data['name'], _description)


class GrocyStockItem:
    def __init__(self, gid, name, stock, stock_opened, min_stock, stock_unit_id, stock_unit):
        self.id = gid
        self.name = name
        self.stock = stock
        self.stock_opened = stock_opened
        self.min_stock = min_stock
        self.stock_unit_id = stock_unit_id
        self.stock_unit = stock_unit

    def __str__(self):
        return f"{self.stock}"

    @classmethod
    def from_json(cls, data):
        return cls(data["product"]["id"], data["product"]["name"], data["stock_amount_aggregated"], data["stock_amount_opened"], data["product"]["min_stock_amount"], data["product"]["qu_id_stock"], data["quantity_unit_stock"]["name"])


class GrocyUnit:
    def __init__(self, gid, name):
        self.mid = gid
        self.name = name

    @classmethod
    def from_json(cls, data):
        return cls(data["id"], data["name"])
