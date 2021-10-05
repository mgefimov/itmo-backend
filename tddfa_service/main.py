import sys;

sys.path.append('./TDDFA_V2');
sys.path.append('.')
sys.path.append('./proto')
import imageio
from TDDFA_V2.TDDFA import TDDFA
from TDDFA_V2.FaceBoxes import FaceBoxes
import numpy as np
import cv2
from proto import model_pb2, model_pb2_grpc
import grpc
from concurrent import futures
import logging


def process_video(filename: str) -> list:
    reader = imageio.get_reader(filename)

    face_boxes = FaceBoxes()
    tddfa = TDDFA(
        arch='mobilenet',
        widen_factor=0.5,
        checkpoint_fp='TDDFA_V2/weights/mb05_120x120.pth',
        bfm_fp='TDDFA_V2/configs/bfm_noneck_v3.pkl',
        size=120,
        num_params=62
    )
    dense_flag = False
    ver_bfm = np.array(
        [
            tddfa.bfm.u_base[0::3][:, 0] / 1000.0,
            tddfa.bfm.u_base[1::3][:, 0] / 1000.0,
            tddfa.bfm.u_base[2::3][:, 0] / 1000.0,
        ]
    )

    transformations = []

    pre_ver = None
    for i, frame in enumerate(reader):
        from PIL import Image
        # im = Image.fromarray(frame)
        # im.save(f'./{i}.jpg')
        frame_bgr = frame[..., ::-1]  # RGB->BGR

        if i == 0:
            # the first frame, detect face, here we only use the first face, you can change depending on your need
            boxes = face_boxes(frame_bgr)
            boxes = [boxes[0]]
            param_lst, roi_box_lst = tddfa(frame_bgr, boxes)
            ver = tddfa.recon_vers(param_lst, roi_box_lst, dense_flag=dense_flag)[0]

            # refine
            param_lst, roi_box_lst = tddfa(frame_bgr, [ver], crop_policy='landmark')
            ver = tddfa.recon_vers(param_lst, roi_box_lst, dense_flag=dense_flag)[0]
        else:
            param_lst, roi_box_lst = tddfa(frame_bgr, [pre_ver], crop_policy='landmark')

            roi_box = roi_box_lst[0]
            # todo: add confidence threshold to judge the tracking is failed
            if abs(roi_box[2] - roi_box[0]) * abs(roi_box[3] - roi_box[1]) < 2020:
                boxes = face_boxes(frame_bgr)
                boxes = [boxes[0]]
                param_lst, roi_box_lst = tddfa(frame_bgr, boxes)

            ver = tddfa.recon_vers(param_lst, roi_box_lst, dense_flag=dense_flag)[0]

        size = frame_bgr.shape
        center = size[1] / 2, size[0] / 2
        points_2D = np.array(
            [
                ver[0],
                ver[1]
            ]
        ).T
        points_3D = np.array(
            [ver_bfm[0], ver_bfm[1], ver_bfm[2]]
        ).T
        dist_coeffs = np.zeros((4, 1))
        focal_length = size[1]
        camera_matrix = np.array(
            [[focal_length, 0, center[0]],
             [0, focal_length, center[1]],
             [0, 0, 1]], dtype="double"
        )
        _, rotation_vector, translation_vector = cv2.solvePnP(points_3D, points_2D, camera_matrix, dist_coeffs)

        # print(f'[{rotation_vector.T[0][0]},{rotation_vector.T[0][1]},{rotation_vector.T[0][2]}],')
        T = np.append(np.concatenate((cv2.Rodrigues(rotation_vector)[0], translation_vector), axis=1), [0, 0, 0, 1])
        transformations.append(T.tolist())

        pre_ver = ver  # for tracking
    return transformations


class Server(model_pb2_grpc.ModelServicer):
    def Run(self, request, context):
        matrices = process_video(request.file_url)
        response = model_pb2.Response()
        for matrix in matrices:
            reshaped = np.array(matrix).reshape(4, 4)
            rotv = cv2.Rodrigues(reshaped[:3, :3])[0]
            row = response.row.add()
            row.rotation.extend(rotv)
            row.transformation.extend(matrix)
        return response


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    model_pb2_grpc.add_ModelServicer_to_server(Server(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    # logging.basicConfig()
    # serve()
    files = ['test01', 'test02', 'test03', 'test04', 'test05', 'test06', 'test07', 'test08', 'test09', 'test10',
             'test11', 'test12', 'test13']
    for file_name in files:
        matrices = process_video(f'./resources/{file_name}.mp4')
        res = '['
        sep = ''
        for matrix in matrices:
            reshaped = np.array(matrix).reshape(4, 4)
            rotv = cv2.Rodrigues(reshaped[:3, :3])[0]
            res += f'{sep}{{ "rotation": [{rotv.T[0][0]},{rotv.T[0][1]},{rotv.T[0][2]}], "transformation": {matrix}}}'
            sep = ',\n'
        res += ']'
        with open(f'./output/{file_name}.json', 'w') as f:
            f.write(res)
