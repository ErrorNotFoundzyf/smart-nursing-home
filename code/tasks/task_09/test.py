#!/usr/bin/env python
# coding: utf-8
'''
表情识别推理
用法: python3 tasks/task_09/test.py
'''

import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"  # 禁用 GPU

import sys
import cv2
import time
import numpy as np
import imutils

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CODE_DIR = os.path.dirname(os.path.dirname(BASE_DIR))
if CODE_DIR not in sys.path:
    sys.path.insert(0, CODE_DIR)

# 共享目录
OLD_CARE_HOME = os.path.dirname(CODE_DIR)
SHARED_MODELS = os.path.join(OLD_CARE_HOME, 'models')
SHARED_IMAGES = os.path.join(OLD_CARE_HOME, 'images')

from keras.preprocessing.image import img_to_array
from keras.models import load_model
from oldcare.facial import FaceUtil

use_gui = os.environ.get('DISPLAY') is not None

# 模型路径（使用共享预训练模型）
model_path = os.path.join(SHARED_MODELS, 'face_expression.hdf5')
input_video = os.path.join(BASE_DIR, 'tests', 'test.mp4')

# 超参数
FACIAL_EXPRESSION_TARGET_WIDTH = 28
FACIAL_EXPRESSION_TARGET_HEIGHT = 28

# 输出目录
output_dir = os.path.join(BASE_DIR, 'detected_faces')
os.makedirs(output_dir, exist_ok=True)

# 加载模型
print('[INFO] 加载表情识别模型...')
model = load_model(model_path)

# 设置视频源
if not os.path.exists(input_video):
    camera = cv2.VideoCapture(0)
    time.sleep(2)
else:
    camera = cv2.VideoCapture(input_video)

faceutil = FaceUtil()

frame_count = 0
smile_count = 0
neutral_count = 0

print('[INFO] 开始表情识别...')
while True:
    (grabbed, frame) = camera.read()

    if not grabbed:
        break

    frame = imutils.resize(frame, width=600)

    face_location_list = faceutil.get_face_location(frame)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    for (left, top, right, bottom) in face_location_list:
        roi = gray[top:bottom, left:right]
        roi = cv2.resize(roi, (FACIAL_EXPRESSION_TARGET_WIDTH,
                               FACIAL_EXPRESSION_TARGET_HEIGHT))
        roi = roi.astype("float") / 255.0
        roi = img_to_array(roi)
        roi = np.expand_dims(roi, axis=0)

        (neutral, smile) = model.predict(roi, verbose=0)[0]
        label = "Neutral" if neutral > smile else "Smile"

        if label == "Smile":
            smile_count += 1
        else:
            neutral_count += 1

        cv2.putText(frame, label, (left, top - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
        cv2.rectangle(frame, (left, top), (right, bottom),
                      (0, 0, 255), 2)

    # 每30帧保存一次检测结果
    if frame_count % 30 == 0 and face_location_list:
        out_path = os.path.join(output_dir, 'frame_%04d.jpg' % frame_count)
        cv2.imwrite(out_path, frame)

    if use_gui:
        cv2.imshow("Facial Expression Detect", frame)
        k = cv2.waitKey(100) & 0xff
        if k == 27:
            break

    frame_count += 1
    if frame_count >= 200:  # 限制处理帧数
        break

camera.release()
if use_gui:
    cv2.destroyAllWindows()

print('[INFO] 处理完成')
print('总帧数: %d, Smile: %d, Neutral: %d' % (frame_count, smile_count, neutral_count))
