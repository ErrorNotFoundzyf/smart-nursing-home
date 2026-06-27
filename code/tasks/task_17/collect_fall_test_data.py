# -*- coding: utf-8 -*-
'''
任务17：老人摔倒检测-测试数据收集

从测试视频中提取帧，使用训练好的 MiniVGGNet 模型自动分类
为 fall（摔倒）和 normal（未摔倒），存入对应文件夹。

用法：python3 tasks/task_17/collect_fall_test_data.py
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

TARGET_WIDTH = 64
TARGET_HEIGHT = 64

model_path = os.path.join(OLD_CARE_HOME, 'models', 'fall_detection.hdf5')
videos_dir = os.path.join(OLD_CARE_HOME, 'images', 'tests', 'videos')

fall_dir = os.path.join(BASE_DIR, 'fall')
normal_dir = os.path.join(BASE_DIR, 'normal')
os.makedirs(fall_dir, exist_ok=True)
os.makedirs(normal_dir, exist_ok=True)

# 测试视频列表
test_videos = [
    'corridor_01.avi',
    'corridor_02.avi',
    'room_04.avi',
    'yard_01.mp4',
    'desk_01.mp4',
    'room_01.mp4',
]

print('[INFO] 加载摔倒检测模型...')
model = load_model(model_path)

total_saved = 0
fall_count = 0
normal_count = 0

for video_name in test_videos:
    video_path = os.path.join(videos_dir, video_name)
    if not os.path.exists(video_path):
        print('[WARN] 视频不存在: %s' % video_path)
        continue

    vs = cv2.VideoCapture(video_path)
    total_frames = int(vs.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = vs.get(cv2.CAP_PROP_FPS)

    # 每个视频取约50帧
    sample_interval = max(1, total_frames // 50)
    print('[INFO] %s: %d 帧, 每 %d 帧采样一次' % (video_name, total_frames, sample_interval))

    frame_idx = 0
    saved_from_video = 0

    while True:
        (grabbed, frame) = vs.read()
        if not grabbed:
            break

        if frame_idx % sample_interval != 0:
            frame_idx += 1
            continue

        # 模型预测
        roi = cv2.resize(frame, (TARGET_WIDTH, TARGET_HEIGHT))
        roi = roi.astype('float') / 255.0
        roi = img_to_array(roi)
        roi = np.expand_dims(roi, axis=0)

        (fall_prob, normal_prob) = model.predict(roi, verbose=0)[0]
        is_fall = fall_prob > normal_prob

        video_prefix = os.path.splitext(video_name)[0]
        out_name = '%s_%04d.jpg' % (video_prefix, frame_idx)
        label = 'Fall (%.2f)' % fall_prob if is_fall else 'Normal (%.2f)' % normal_prob

        if is_fall:
            out_path = os.path.join(fall_dir, out_name)
            fall_count += 1
        else:
            out_path = os.path.join(normal_dir, out_name)
            normal_count += 1

        cv2.putText(frame, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.imwrite(out_path, frame)
        saved_from_video += 1
        total_saved += 1

        frame_idx += 1
        if saved_from_video >= 50:
            break

    vs.release()
    print('  保存 %d 帧' % saved_from_video)

print('\n[INFO] 数据收集完成！')
print('  总计: %d 张' % total_saved)
print('  fall/: %d 张' % fall_count)
print('  normal/: %d 张' % normal_count)
