import sys
sys.path.append('.')
from ...items import read_item, Item
from ...proto import model_pb2, model_pb2_grpc
import grpc
from concurrent import futures
import configparser
config = configparser.ConfigParser()
config.read('./config.ini')


def test_apply_discount():
    item = read_item(1)
    discount_item = Item(**item.dict())
    assert discount_item.is_valid()
    discount_item.apply_discount()
    assert discount_item.price == 80.0


def test_read_unknown_item():
    item = read_item(666)
    assert item is None


def test_invalid_item():
    item = read_item(2)
    item.price -= 1000
    discount_item = Item(**item.dict())
    assert discount_item.is_valid() is False


def test_tddfa_service():
    class Server(model_pb2_grpc.ModelServicer):
        def Run(self, request, context):
            response = model_pb2.Response()
            row = response.row.add()
            row.rotation.extend([1, 2, 3])
            row.transformation.extend([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16])
            return response

    def serve():
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        model_pb2_grpc.add_ModelServicer_to_server(Server(), server)
        server.add_insecure_port(f'[::]:{config["tddfa"]["port"]}')
        server.start()

    serve()
    with grpc.insecure_channel(f'{config["tddfa"]["host"]}:{config["tddfa"]["port"]}') as channel:
        stub = model_pb2_grpc.ModelStub(channel)
        response = stub.Run(model_pb2.Request(file_url='test_file'))
        assert response.row[0].rotation[1] == 2
        assert response.row[0].transformation[15] == 16
