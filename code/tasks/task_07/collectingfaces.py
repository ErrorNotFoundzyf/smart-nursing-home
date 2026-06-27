# -*- coding: utf-8 -*-
'''
图像采集程序-人脸检测

用法：
  python3 tasks/task_07/collectingfaces.py --id 106 --imagedir ./captured_faces
  id：老人/员工/义工的唯一id
  imagedir：储存图像的路径
'''

import argparse
import os
import sys

# 将 code/ 目录加入路径，确保 oldcare 库可导入
CODE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if CODE_DIR not in sys.path:
    sys.path.insert(0, CODE_DIR)

from oldcare.facial import FaceUtil
from oldcare.audio import audioplayer
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
import shutil
import time
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OLD_CARE_HOME = os.path.abspath(os.path.join(BASE_DIR, '..', '..', '..'))  # old_care_system/

# 实例化类
faceutil = FaceUtil()

# 全局参数
audio_dir = os.path.join(OLD_CARE_HOME, 'audios')
font_path = '/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc'
use_gui = os.environ.get('DISPLAY') is not None

# 传入参数
ap = argparse.ArgumentParser()
ap.add_argument("-ic", "--id", required=True, help="人员ID")
ap.add_argument("-id", "--imagedir", default=os.path.join(BASE_DIR, 'captured_faces'),
                help="图像保存路径")
args = vars(ap.parse_args())

# 新建目录
save_dir = os.path.join(args['imagedir'], args['id'])
if os.path.exists(save_dir):
    shutil.rmtree(save_dir, True)
os.makedirs(save_dir, exist_ok=True)

# 人脸采集的动作
action_list = ['blink', 'open_mouth', 'smile', 'rise_head', 'bow_head',
               'look_left', 'look_right']
action_map = {'blink': '请眨眼', 'open_mouth': '请张嘴',
              'smile': '请笑一笑', 'rise_head': '请抬头',
              'bow_head': '请低头', 'look_left': '请看左边',
              'look_right': '请看右边'}


# 如果不方便打开摄像头，则用视频模拟
video_path = os.path.join(BASE_DIR, 'test.mp4')
# video_path = ''

# 设置摄像头
if os.path.exists(video_path):
    cam = cv2.VideoCapture(video_path)
else:
    cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)


# 图像预采集
error = 0
start_time = None
limit_time = 2
frame_count = 0

print('[INFO] 正在预采集，请面对摄像头...')
while True:
    frame_count += 1
    ret, image = cam.read()
    if not ret:
        print("视频结束，未检测到有效人脸")
        break
    if frame_count <= 10:
        continue
    image = cv2.flip(image, 1)

    if error == 1:
        end_time = time.time()
        if end_time - start_time >= limit_time:
            error = 0

    face_location_list = faceutil.get_face_location(image)
    for (left, top, right, bottom) in face_location_list:
        cv2.rectangle(image, (left, top), (right, bottom), (0, 0, 255), 2)

    if use_gui:
        cv2.imshow('Collecting Faces', image)
        k = cv2.waitKey(100) & 0xff
        if k == 27:
            break

    face_count = len(face_location_list)
    if error == 0 and face_count == 0:
        print('[WARNING] 没有检测到人脸')
        audioplayer.play_audio(os.path.join(audio_dir, 'no_face_detected.mp3'))
        error = 1
        start_time = time.time()
    elif error == 0 and face_count == 1:
        print('[INFO] 可以开始采集图像了')
        audioplayer.play_audio(os.path.join(audio_dir, 'start_image_capturing.mp3'))
        break
    elif error == 0 and face_count > 1:
        print('[WARNING] 检测到多张人脸')
        audioplayer.play_audio(os.path.join(audio_dir, 'multi_faces_detected.mp3'))
        error = 1
        start_time = time.time()


# 开始正式采集人脸
for action in action_list:
    audioplayer.play_audio(os.path.join(audio_dir, action + '.mp3'))
    action_name = action_map[action]

    for i in range(15):
        print('正在采集：%s-%d' % (action_name, i))
        ret, img_OpenCV = cam.read()
        if not ret:
            break
        img_OpenCV = cv2.flip(img_OpenCV, 1)
        origin_img = img_OpenCV.copy()

        # 人脸检测
        face_location_list = faceutil.get_face_location(img_OpenCV)
        for (left, top, right, bottom) in face_location_list:
            cv2.rectangle(img_OpenCV, (left, top), (right, bottom), (0, 0, 255), 2)

        # 在画面中显示中文动作提示
        try:
            img_PIL = Image.fromarray(cv2.cvtColor(img_OpenCV, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(img_PIL)
            draw.text((int(image.shape[1] / 2), 30), action_name,
                      font=ImageFont.truetype(font_path, 40), fill=(255, 0, 0))
            img_OpenCV = cv2.cvtColor(np.asarray(img_PIL), cv2.COLOR_RGB2BGR)
        except Exception as e:
            print(f"  字体渲染跳过: {e}")

        if use_gui:
            cv2.imshow('Collecting Faces', img_OpenCV)
            k = cv2.waitKey(100) & 0xff
            if k == 27:
                break

        # 保存原始图像（不叠加显示文字）
        image_name = os.path.join(save_dir, '%s_%d.jpg' % (action, i + 1))
        cv2.imwrite(image_name, origin_img)


# 结束
print('[INFO] 采集完毕，共采集 %d 张人脸图像' % (len(action_list) * 15))
audioplayer.play_audio(os.path.join(audio_dir, 'end_capturing.mp3'))

cam.release()
if use_gui:
    cv2.destroyAllWindows()
