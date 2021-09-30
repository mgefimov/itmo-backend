from fastapi import FastAPI, Response, status
from items import Item, DiscountItem, read_item
from graphene import ObjectType, String, Schema, Int, Field
from starlette.graphql import GraphQLApp
import grpc
import model_pb2
import model_pb2_grpc
from google.protobuf.json_format import MessageToDict

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


@app.get('/process_video/')
def process_video(file_url: str):
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = model_pb2_grpc.ModelStub(channel)
        response = stub.Run(model_pb2.Request(file_url=file_url))
    return MessageToDict(response)


class Pet(ObjectType):
    name = String()
    age = Int()


class Person(ObjectType):
    first_name = String()
    last_name = String()
    pet = Field(Pet)


persons = {
    '123': Person(first_name='Max', last_name="Efimov", pet=Pet(name='Vasya', age=3)),
    '124': Person(first_name='Ivan', last_name="Ivanov", pet=Pet(name='Vasya', age=4))
}


class Query(ObjectType):
    person = Field(Person, uid=String())

    def resolve_person(root, info, uid):
        return persons[uid]


schema = Schema(query=Query)

app.add_route('/graphql', GraphQLApp(schema=schema))
