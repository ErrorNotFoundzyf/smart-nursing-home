# -*- coding: utf-8 -*-
'''
使用dlib实现人脸检测
'''

import face_recognition
import cv2
import time
import os

# 超参数
detection_method = 'hog'  # 参数值为hog/cnn。表示人脸检测使用hog提取特征还是使用cnn提取特征。

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
video_path = os.path.join(BASE_DIR, 'test.mp4')
# video_path = ''
use_gui = os.environ.get('DISPLAY') is not None
max_frames = 200  # 视频文件最多处理200帧
output_dir = os.path.join(BASE_DIR, 'detected_faces')
os.makedirs(output_dir, exist_ok=True)

# 初始化摄像头
if video_path:
    cap = cv2.VideoCapture(video_path)
else:
    cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # 视频宽度
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # 视频高度
time.sleep(2)

frame_count = 0
face_count = 0

while True:
    ret, img = cap.read()
    if not ret:
        print("视频播放结束")
        break

    # 人脸检测不依赖色彩，所以先把人脸图像转成灰度图像
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    face_locations = face_recognition.face_locations(
        gray, number_of_times_to_upsample=1,
        model=detection_method)

    # 用矩形框框出人脸位置
    for (top, right, bottom, left) in face_locations:
        cv2.rectangle(img, (left, top), (right, bottom),
                      (0, 0, 255), 2)
        cv2.rectangle(gray, (left, top), (right, bottom),
                      (0, 0, 255), 2)

    if face_locations:
        face_count += len(face_locations)
        # 保存有人脸的帧
        out_path = os.path.join(output_dir, f'frame_{frame_count:04d}_faces_{len(face_locations)}.jpg')
        cv2.imwrite(out_path, img)
        print(f"第{frame_count}帧: 检测到{len(face_locations)}张人脸 → 已保存")

    if use_gui:
        cv2.imshow('original image', img)
        cv2.imshow('gray image', gray)
        # 按 'ESC' 键终止
        k = cv2.waitKey(1) & 0xff
        if k == 27:
            break

    frame_count += 1
    # 视频文件限制帧数
    if video_path and frame_count >= max_frames:
        print(f"已达最大处理帧数({max_frames})")
        break

cap.release()
if use_gui:
    cv2.destroyAllWindows()
print(f"任务2完成：共处理{frame_count}帧，检测到{face_count}张人脸")
print(f"检测结果已保存至 {output_dir}/")