from fastapi import FastAPI, Response, status, File, UploadFile
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from uuid import uuid4

app = FastAPI()

app.mount('/static', StaticFiles(directory='static'), name='static')

host = 'http://127.0.0.1:8000'


@app.get('/')
def read_root():
    return {'Hello': 'World'}


@app.post('/upload_file')
async def upload_file(file: UploadFile = File(...)):
    extension = file.filename.split('.')[1]
    folder = './static'
    filename = f"{str(uuid4())}.{extension}"
    b = await file.read()
    with open(f"{folder}/{filename}", 'wb') as f:
        f.write(b)
    url = f"{host}/static/{filename}"
    return {'url': url}


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

    def apply_discount(self):
        self.price *= 0.8
        self.item_name += '(Скидка)'

    def is_valid(self):
        return self.price >= 0


@app.post('/get_discount/')
def get_discount(item: DiscountItem, response: Response):
    if not item.is_valid():
        response.status_code = status.HTTP_412_PRECONDITION_FAILED
        return {'success': False, 'error': 'the price should be positive'}
    item.apply_discount()
    return {'success': True, 'data': item}
