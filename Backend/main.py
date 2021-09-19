from typing import List
from fastapi import FastAPI, File
from pydantic import BaseModel
from pathlib import Path
import uuid
import imageio
import sys
sys.path.append('./TDDFA_V2/')
from TDDFA_V2.TDDFA import TDDFA
from TDDFA_V2.FaceBoxes import FaceBoxes
import numpy as np
import cv2

app = FastAPI()


@app.get('/')
def read_root():
    return {'Hello': 'World'}


@app.post('/videos/{uid}')
def process_video(uid: str, b: bytes = File(...)):
    Path('./tmp/').mkdir(parents=True, exist_ok=True)
    filename = './tmp/' + str(uuid.uuid4()) + '.mp4'
    with open(filename, 'wb') as f:
        f.write(b)
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
        T = np.append(np.concatenate((cv2.Rodrigues(rotation_vector)[0], translation_vector), axis=1), [0, 0, 0, 1])
        print(T)
        transformations.append(T.tolist())

        pre_ver = ver  # for tracking
    return {'uid': uid, 'frames': transformations}


class Response(BaseModel):
    uid: str
    frames: List[List[float]]


@app.get('/videos/{uid}')
def get_video(uid: str):
    resp = Response(uid=uid, frames=[[
      0.9344910352899486,
      0.30957304030809835,
      -0.1757584640269728,
      39.250220027501484,
      0.3407160498708474,
      -0.920846142500402,
      0.1896179189911536,
      4.939824564118907,
      -0.10314590793204745,
      -0.2370799750222063,
      -0.96599896848824,
      516.1355631725884,
      0,
      0,
      0,
      1
    ], [
      0.930654234488134,
      0.31956648838704643,
      -0.1782132299501852,
      39.715060259709105,
      0.351843918822688,
      -0.9152826948562577,
      0.19612099654081044,
      3.869270446078736,
      -0.10044178720432859,
      -0.24522407711445987,
      -0.96424924132019,
      515.1614867896812,
      0,
      0,
      0,
      1
    ]])
    return resp
