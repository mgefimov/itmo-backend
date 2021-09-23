from pydantic import BaseModel


class Item(BaseModel):
    name: str
    price: float


items = {
    123: Item(name=f'item 123', price=100.0),
    124: Item(name=f'item 124', price=200.0),
    125: Item(name=f'item 124', price=350.0),
}


class DiscountItem(BaseModel):
    username: str
    price: float
    name: str

    def apply_discount(self):
        self.price *= 0.8
        self.name += '(Скидка)'

    def is_valid(self):
        return self.price >= 0


def read_item(item_id: int):
    if item_id in items:
        return items[item_id]
    return None
