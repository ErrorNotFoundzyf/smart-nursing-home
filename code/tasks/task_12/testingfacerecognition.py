# -*- coding: utf-8 -*-
'''
测试人脸识别模型

用法：
  python3 tasks/task_12/testingfacerecognition.py
  python3 tasks/task_12/testingfacerecognition.py --filename room_01.mp4
'''

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CODE_DIR = os.path.dirname(os.path.dirname(BASE_DIR))
if CODE_DIR not in sys.path:
    sys.path.insert(0, CODE_DIR)

OLD_CARE_HOME = os.path.dirname(CODE_DIR)

from oldcare.facial import FaceUtil
import imutils
import cv2
import time
import argparse

use_gui = os.environ.get('DISPLAY') is not None

# 传入参数
ap = argparse.ArgumentParser()
ap.add_argument("-f", "--filename", required=False, default='',
                help="输入视频文件路径")
args = vars(ap.parse_args())

# 全局变量
facial_recognition_model_path = os.path.join(
    OLD_CARE_HOME, 'models', 'face_recognition_hog.pickle')
input_video = args['filename']
output_dir = os.path.join(BASE_DIR, 'detected_faces')
os.makedirs(output_dir, exist_ok=True)

# 初始化摄像头/视频
if input_video:
    if not os.path.isabs(input_video):
        input_video = os.path.join(BASE_DIR, input_video)
    vs = cv2.VideoCapture(input_video)
else:
    vs = cv2.VideoCapture(0)
    time.sleep(2)

# 初始化人脸识别模型
faceutil = FaceUtil(facial_recognition_model_path)
faceutil.detection_method = 'hog'  # CNN 在 CPU 上太慢，使用 HOG

frame_count = 0
while True:
    (grabbed, frame) = vs.read()
    if input_video and not grabbed:
        break
    if not input_video:
        frame = cv2.flip(frame, 1)

    frame = imutils.resize(frame, width=600)
    face_location_list, names = faceutil.get_face_location_and_name(frame)

    for ((left, top, right, bottom), name) in zip(face_location_list, names):
        cv2.putText(frame, name, (left, top - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.rectangle(frame, (left, top), (right, bottom),
                      (0, 0, 255), 2)

    # 保存检测结果帧
    if face_location_list and frame_count % 30 == 0:
        names_str = '_'.join(names)
        out_path = os.path.join(output_dir, 'frame_%04d_%s.jpg' % (frame_count, names_str.replace(' ', '_')))
        cv2.imwrite(out_path, frame)
        print('第%d帧: 检测到 %s' % (frame_count, names))

    if use_gui:
        cv2.imshow("Face Recognition", frame)
        k = cv2.waitKey(1) & 0xff
        if k == 27:
            break

    frame_count += 1
    if frame_count >= 200:
        break

vs.release()
if use_gui:
    cv2.destroyAllWindows()
print('[INFO] 人脸识别测试完成，处理 %d 帧' % frame_count)
