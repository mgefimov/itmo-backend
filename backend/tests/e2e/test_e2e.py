import sys
sys.path.append('.')
from ...main import app, schema
from fastapi.testclient import TestClient
from graphene.test import Client

client = TestClient(app)


def test_read_main():
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {'Hello': 'World'}


def test_get_item():
    response = client.get('/items/1')
    assert response.status_code == 200
    assert response.json()['name'] == 'item 123'
    assert response.json()['price'] == 100.0


def test_get_discount():
    response = client.post('/get_discount/',
                           json={
                               'username': 'test name',
                               'name': 'test item',
                               'price': -123
                           })
    assert response.status_code == 412
    assert response.json()['success'] is False

    response = client.post('/get_discount/',
                           json={
                               'username': 'test name',
                               'name': 'test item',
                               'price': 100
                           })
    assert response.status_code == 200
    json = response.json()
    data = json['data']
    assert json['success'] is True
    assert data['price'] == 80.0
    assert data['name'].endswith('(Скидка)')


def test_graphql():
    client = Client(schema)
    executed = client.execute('''{
  person(uid:"123"){
    firstName
    pet {
      name
      age
    }
  }
}''')
    data = executed['data']
    assert data['person']['firstName'] == 'Max'
    assert data['person']['pet']['age'] == 3


def test_graphql_no_pet():
    client = Client(schema)
    executed = client.execute('''{
  person(uid:"124"){
    firstName
  }
}''')
    data = executed['data']
    assert data['person']['firstName'] == 'Ivan'
    assert 'pet' not in data['person']
