from ...main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_read_main():
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {'Hello': 'World'}


def test_get_item():
    response = client.get('/items/123')
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
