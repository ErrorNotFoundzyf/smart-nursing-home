# -*- coding: utf-8 -*-
'''
摔倒检测测试
用法：
  python3 tasks/task_16/testingfalldetection.py
  python3 tasks/task_16/testingfalldetection.py --filename corridor_01.avi
'''

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CODE_DIR = os.path.dirname(os.path.dirname(BASE_DIR))
if CODE_DIR not in sys.path:
    sys.path.insert(0, CODE_DIR)

OLD_CARE_HOME = os.path.dirname(CODE_DIR)

from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
import numpy as np
import cv2
import time
import argparse

use_gui = os.environ.get('DISPLAY') is not None

ap = argparse.ArgumentParser()
ap.add_argument("-f", "--filename", required=False, default='', help="输入视频")
args = vars(ap.parse_args())
input_video = args['filename']

# 模型路径
model_path = os.path.join(OLD_CARE_HOME, 'models', 'fall_detection.hdf5')
TARGET_WIDTH = 64
TARGET_HEIGHT = 64

# 输出目录
output_dir = os.path.join(BASE_DIR, 'detected_falls')
os.makedirs(output_dir, exist_ok=True)

# 初始化视频源
if input_video:
    if not os.path.isabs(input_video):
        input_video = os.path.join(OLD_CARE_HOME, 'images', 'tests', 'videos', input_video)
    vs = cv2.VideoCapture(input_video)
    print('[INFO] 视频: %s' % input_video)
else:
    vs = cv2.VideoCapture(0)
    time.sleep(2)

# 加载模型
print('[INFO] 加载摔倒检测模型...')
model = load_model(model_path)

print('[INFO] 开始检测是否有人摔倒...')
frame_count = 0
fall_frames = 0

while True:
    (grabbed, image) = vs.read()
    if input_video and not grabbed:
        break
    if not input_video:
        image = cv2.flip(image, 1)

    # 整帧缩放到64x64作为模型输入
    roi = cv2.resize(image, (TARGET_WIDTH, TARGET_HEIGHT))
    roi = roi.astype("float") / 255.0
    roi = img_to_array(roi)
    roi = np.expand_dims(roi, axis=0)

    (fall_prob, normal_prob) = model.predict(roi, verbose=0)[0]
    is_fall = fall_prob > normal_prob
    label = "Fall (%.2f)" % fall_prob if is_fall else "Normal (%.2f)" % normal_prob

    if is_fall:
        fall_frames += 1

    cv2.putText(image, label, (image.shape[1] - 180, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    # 保存有摔倒的帧
    if is_fall and frame_count % 10 == 0:
        out_path = os.path.join(output_dir, 'fall_%04d.jpg' % frame_count)
        cv2.imwrite(out_path, image)

    if use_gui:
        cv2.imshow('Fall detection', image)
        k = cv2.waitKey(1) & 0xff
        if k == 27:
            break

    frame_count += 1
    if frame_count >= 300:
        break

vs.release()
if use_gui:
    cv2.destroyAllWindows()
print('[INFO] 检测完成: 共 %d 帧, 检测到 %d 帧为摔倒(%.1f%%)' % (
    frame_count, fall_frames, fall_frames / frame_count * 100 if frame_count else 0))
