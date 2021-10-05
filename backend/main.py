import sys
sys.path.append('./proto')
from .graphql import Query
from fastapi import FastAPI, Response, status
from items import Item, read_item
from graphene import Schema
from starlette.graphql import GraphQLApp
import grpc
from proto import model_pb2, model_pb2_grpc
from google.protobuf.json_format import MessageToDict

app = FastAPI()


@app.get('/')
def read_root():
    return {'Hello': 'World'}


@app.get('/items/{item_id}', response_model=Item)
def get_item(item_id: int):
    return read_item(item_id)


@app.post('/get_discount/')
def get_discount(item: Item, response: Response):
    if not item.is_valid():
        response.status_code = status.HTTP_412_PRECONDITION_FAILED
        return {'success': False, 'error': 'the price should be positive'}
    item.apply_discount()
    return {'success': True, 'data': item}


@app.get('/process_video/')
def process_video(file_url: str):
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = model_pb2_grpc.ModelStub(channel)
        response = stub.Run(model_pb2.Request(file_url=file_url))
    return MessageToDict(response)


schema = Schema(query=Query)

app.add_route('/graphql', GraphQLApp(schema=schema))
