from pydantic import BaseModel
import psycopg2

conn = psycopg2.connect(
    user='itmouser',
    dbname='itmodb',
    password='pgpwd4itmo',
    host='localhost',
)


class Item(BaseModel):
    name: str
    price: float

    def apply_discount(self):
        self.price *= 0.8
        self.name += '(Скидка)'

    def is_valid(self):
        return self.price >= 0


def read_item(item_id: int):
    cursor = conn.cursor()
    cursor.execute('select * from items where id=%s', (item_id,))
    res = cursor.fetchone()
    if res is not None:
        return Item(name=res[1], price=float(res[2][1:]))
    return None
