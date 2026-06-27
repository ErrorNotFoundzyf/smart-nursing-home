# -*- coding: utf-8 -*-
'''
任务20：老人义工互动检测

通过人脸识别识别义工和老人，计算两者面部质心距离，
距离 < 100cm 时判定为互动，记录事件并保存快照。

用法：python3 tasks/task_20/testingvolunteeractivity.py
      python3 tasks/task_20/testingvolunteeractivity.py --filename desk_01.mp4
'''

import os
import sys
import time
import argparse
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CODE_DIR = os.path.dirname(os.path.dirname(BASE_DIR))
if CODE_DIR not in sys.path:
    sys.path.insert(0, CODE_DIR)

OLD_CARE_HOME = os.path.dirname(CODE_DIR)

from oldcare.facial import FaceUtil
from oldcare.utils import fileassistant
from scipy.spatial import distance as dist
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import imutils
import cv2

use_gui = os.environ.get('DISPLAY') is not None

ap = argparse.ArgumentParser()
ap.add_argument("-f", "--filename", default='', help="测试视频文件名")
args = vars(ap.parse_args())

model_path       = os.path.join(OLD_CARE_HOME, 'models', 'face_recognition_hog.pickle')
people_info_path = os.path.join(OLD_CARE_HOME, 'info', 'people_info.csv')
font_path        = '/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc'
snapshot_dir     = os.path.join(BASE_DIR, 'supervision', 'volunteer')
os.makedirs(snapshot_dir, exist_ok=True)

# Database insertion integration
task_22_dir = os.path.join(CODE_DIR, 'tasks', 'task_22')
inserting_script = os.path.join(task_22_dir, 'inserting.py')
allow_file = os.path.join(task_22_dir, 'allowinsertdatabase.txt')

def trigger_db_insert(event_desc, event_type, event_location, old_people_id=''):
    with open(allow_file, 'w') as f:
        f.write('is_allowed=1')
    cmd = [sys.executable, inserting_script,
           '--event_desc', event_desc,
           '--event_type', str(event_type),
           '--event_location', event_location]
    if old_people_id:
        cmd += ['--old_people_id', str(old_people_id)]
    subprocess.Popen(cmd)

input_video = args['filename']
if input_video and not os.path.isabs(input_video):
    input_video = os.path.join(OLD_CARE_HOME, 'images', 'tests', 'videos', input_video)

FACE_ACTUAL_WIDTH    = 20   # cm
VIDEO_WIDTH          = 640
ACTUAL_DISTANCE_LIMIT = 100 # cm

id_card_to_name, id_card_to_type = fileassistant.get_people_info(people_info_path)

if not input_video:
    vs = cv2.VideoCapture(0)
    time.sleep(2)
else:
    print('[INFO] 打开视频: %s' % input_video)
    vs = cv2.VideoCapture(input_video)

print('[INFO] 加载人脸识别模型...')
faceutil = FaceUtil(model_path)

print('[INFO] 开始检测义工和老人是否有互动...')
frame_count = interaction_count = 0

try:
    font = ImageFont.truetype(font_path, 28)
except:
    font = ImageFont.load_default()

while True:
    (grabbed, frame) = vs.read()
    if input_video and not grabbed:
        break
    if not input_video:
        frame = cv2.flip(frame, 1)

    frame = imutils.resize(frame, width=VIDEO_WIDTH)
    face_location_list, names = faceutil.get_face_location_and_name(frame)

    if not face_location_list:
        frame_count += 1
        if frame_count >= 300:
            break
        continue

    people_types = set(id_card_to_type.get(n, '') for n in names)

    volunteer_centroids = []
    old_people_centroids = []
    old_people_names = []

    for ((left, top, right, bottom), name) in zip(face_location_list, names):
        ptype = id_card_to_type.get(name, '')
        color = {'old_people': (0, 0, 128), 'employee': (255, 0, 0),
                 'volunteer': (0, 255, 0)}.get(ptype, (0, 0, 255))
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

        cx, cy = (left + right) // 2, (top + bottom) // 2
        if ptype == 'volunteer':
            volunteer_centroids.append((cx, cy))
            cv2.circle(frame, (cx, cy), 8, (255, 0, 0), -1)
        elif ptype == 'old_people':
            old_people_centroids.append((cx, cy))
            old_people_names.append(name)
            cv2.circle(frame, (cx, cy), 4, (0, 255, 0), -1)

        # 中文标注
        img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        ImageDraw.Draw(img_pil).text((left, max(0, top - 32)),
                                     id_card_to_name.get(name, name),
                                     font=font, fill=(255, 0, 0))
        frame = cv2.cvtColor(np.asarray(img_pil), cv2.COLOR_RGB2BGR)

    # 计算义工与老人距离
    if volunteer_centroids and old_people_centroids:
        face_widths = [r - l for (l, t, r, b) in face_location_list]
        pixel_per_metric = (sum(face_widths) / len(face_widths)) / FACE_ACTUAL_WIDTH

        for vc in volunteer_centroids:
            for idx, oc in enumerate(old_people_centroids):
                pixel_dist = dist.euclidean(vc, oc)
                actual_dist = pixel_dist / pixel_per_metric

                if actual_dist < ACTUAL_DISTANCE_LIMIT:
                    cv2.line(frame, vc, oc, (255, 0, 255), 2)
                    cv2.putText(frame, 'dist: %dcm' % actual_dist,
                                (frame.shape[1] - 160, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

                    ts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                    old_name = id_card_to_name.get(old_people_names[idx], old_people_names[idx])
                    print('[EVENT] %s 房间桌子 %s 正在与义工交互.' % (ts, old_name))

                    if interaction_count % 30 == 0:
                        snap = 'interaction_%s.jpg' % time.strftime('%Y%m%d_%H%M%S')
                        cv2.imwrite(os.path.join(snapshot_dir, snap), frame)
                        trigger_db_insert('%s 正在与义工交互' % old_name, 1, '房间桌子', old_people_names[idx])

                    interaction_count += 1

    if use_gui:
        cv2.imshow("Volunteer Activity", frame)
        if cv2.waitKey(1) & 0xff == 27:
            break

    frame_count += 1
    if frame_count >= 300:
        break

vs.release()
if use_gui:
    cv2.destroyAllWindows()

print('[INFO] 处理帧数: %d, 检测到互动帧数: %d' % (frame_count, interaction_count))
print('[INFO] 快照保存目录: %s' % snapshot_dir)
