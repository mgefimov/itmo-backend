from fastapi import FastAPI, Response, status
from .items import Item, DiscountItem, read_item

app = FastAPI()


@app.get('/')
def read_root():
    return {'Hello': 'World'}


@app.get('/items/{item_id}', response_model=Item)
def get_item(item_id: int):
    return read_item(item_id)


@app.post('/get_discount/')
def get_discount(item: DiscountItem, response: Response):
    if not item.is_valid():
        response.status_code = status.HTTP_412_PRECONDITION_FAILED
        return {'success': False, 'error': 'the price should be positive'}
    item.apply_discount()
    return {'success': True, 'data': item}
