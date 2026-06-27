# -*- coding: utf-8 -*-
'''
任务13：陌生人识别-测试数据收集（改进版）

从测试视频提取帧，保存完整帧图像（非裁剪），
标注每张人脸在帧中的位置和身份标签，
供任务14做批量评估。
'''

import os
import sys
import csv
import cv2

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CODE_DIR = os.path.dirname(os.path.dirname(BASE_DIR))
if CODE_DIR not in sys.path:
    sys.path.insert(0, CODE_DIR)

OLD_CARE_HOME = os.path.dirname(CODE_DIR)
from oldcare.facial import FaceUtil

MODEL_PATH = os.path.join(OLD_CARE_HOME, 'models', 'face_recognition_hog.pickle')

faceutil = FaceUtil(MODEL_PATH)
faceutil.detection_method = 'hog'

# 视频列表
videos = ['room_01.mp4', 'room_04.avi', 'desk_01.mp4']

output_dir = os.path.join(BASE_DIR, 'test_frames')
os.makedirs(output_dir, exist_ok=True)

csv_path = os.path.join(BASE_DIR, 'test_annotations.csv')
csv_file = open(csv_path, 'w', newline='')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['frame_file', 'face_id', 'label', 'name',
                      'left', 'top', 'right', 'bottom'])

total_faces = 0
known_count = 0
stranger_count = 0

for video_name in videos:
    video_path = os.path.join(OLD_CARE_HOME, 'images', 'tests', 'videos', video_name)
    if not os.path.exists(video_path):
        continue

    vs = cv2.VideoCapture(video_path)
    frame_idx = 0
    saved_frames = 0

    while True:
        ret, frame = vs.read()
        if not ret:
            break

        if frame_idx % 30 != 0:
            frame_idx += 1
            continue

        frame = cv2.resize(frame, (640, 480))

        # 使用模型检测+识别
        face_location_list, names = faceutil.get_face_location_and_name(frame)

        if face_location_list:
            # 保存整帧
            frame_filename = '%s_frame%04d.jpg' % (video_name.replace('.', '_'), frame_idx)
            frame_path = os.path.join(output_dir, frame_filename)
            cv2.imwrite(frame_path, frame)

            for fid, (name, (left, top, right, bottom)) in enumerate(
                zip(names, face_location_list)):

                label = 'stranger' if name == 'Unknown' else 'known'
                csv_writer.writerow([
                    frame_filename, fid, label, name,
                    left, top, right, bottom
                ])
                total_faces += 1
                if label == 'known':
                    known_count += 1
                else:
                    stranger_count += 1

            saved_frames += 1

        frame_idx += 1
        if frame_idx >= 300:
            break

    vs.release()
    print('%s: 保存%d帧, 共%d张人脸' % (video_name, saved_frames, total_faces - (known_count + stranger_count - (known_count + stranger_count))))

csv_file.close()
print()
print('===== 完成 =====')
print('标注帧数: %d' % total_faces)
print('熟人: %d, 陌生人: %d' % (known_count, stranger_count))
print('帧保存目录: %s' % output_dir)
print('标注文件: %s' % csv_path)
