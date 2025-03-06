class Ingredient:
    def __init__(self, name, amount, unit, note=None, mid=None, gid=None):
        self.name = name
        self.amount = amount
        self.unit = unit
        self.note = note
        self.mid = mid
        self.gid = gid

    def add(self, other: 'Ingredient'):
        if self.unit == other.unit:
            self.amount += other.amount

            if self.note:
                self.note += f", {other.note}" if other.note and other.note != self.note else ""
            else:
                self.note = other.note
        else:
            raise ValueError(f"Cannot add ingredients with different units: {self.unit} and {other.unit}")

    @classmethod
    def from_mealie_json(cls, data) -> 'Ingredient | None':
        if data["food"] is None:
            return None

        unit = data["unit"]["name"] if data["unit"] is not None else None

        return cls(data["food"]["name"], data["quantity"], unit, mid=data["food"]["id"])

    def __str__(self):
        text = f"{self.amount} {self.name}"
        if self.unit:
            text = f"{self.amount} {self.unit} {self.name}"
        if self.note:
            text += f" ({self.note})"
        return text

    def __repr__(self):
        return str(self)
