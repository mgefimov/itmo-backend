from fastapi import FastAPI, Response, status
from pydantic import BaseModel

app = FastAPI()


@app.get('/')
def read_root():
    return {'Hello': 'World'}


class Item(BaseModel):
    name: str
    price: float


@app.get('/items/{item_id}', response_model=Item)
def read_item(item_id: int):
    return Item(id=item_id, name=f'item {item_id}', price=100.0)


class DiscountItem(BaseModel):
    username: str
    price: float
    item_name: str


@app.post('/get_discount/')
def get_discount(item: DiscountItem, response: Response):
    if item.price < 0:
        response.status_code = status.HTTP_412_PRECONDITION_FAILED
        return {'success': False, 'error': 'the price should be positive'}
    item.price *= 0.8
    item.item_name += '(Скидка)'
    return {'success': True, 'data': item}
