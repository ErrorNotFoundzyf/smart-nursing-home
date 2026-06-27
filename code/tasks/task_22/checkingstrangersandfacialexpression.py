# -*- coding: utf-8 -*-
'''
任务22整合：陌生人识别 + 老人表情检测（含计时报警 + 数据库写入）

用法：python3 tasks/task_22/checkingstrangersandfacialexpression.py
      python3 tasks/task_22/checkingstrangersandfacialexpression.py --filename room_01.mp4
'''

import os
import sys
import time
import subprocess
import argparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CODE_DIR = os.path.dirname(os.path.dirname(BASE_DIR))
if CODE_DIR not in sys.path:
    sys.path.insert(0, CODE_DIR)

OLD_CARE_HOME = os.path.dirname(CODE_DIR)

from oldcare.facial import FaceUtil
from oldcare.utils import fileassistant
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import imutils
import cv2

use_gui = os.environ.get('DISPLAY') is not None

ap = argparse.ArgumentParser()
ap.add_argument("-f", "--filename", default='')
args = vars(ap.parse_args())
input_video = args['filename']
if input_video and not os.path.isabs(input_video):
    input_video = os.path.join(OLD_CARE_HOME, 'images', 'tests', 'videos', input_video)

face_recog_model  = os.path.join(OLD_CARE_HOME, 'models', 'face_recognition_hog.pickle')
face_expr_model   = os.path.join(OLD_CARE_HOME, 'models', 'face_expression.hdf5')
people_info_path  = os.path.join(OLD_CARE_HOME, 'info', 'people_info.csv')
expr_info_path    = os.path.join(OLD_CARE_HOME, 'info', 'facial_expression_info.csv')
output_stranger   = os.path.join(OLD_CARE_HOME, 'supervision', 'strangers')
output_smile      = os.path.join(OLD_CARE_HOME, 'supervision', 'smile')
allow_file        = os.path.join(BASE_DIR, 'allowinsertdatabase.txt')
inserting_script  = os.path.join(BASE_DIR, 'inserting.py')
font_path         = '/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc'

os.makedirs(output_stranger, exist_ok=True)
os.makedirs(output_smile, exist_ok=True)

EXPR_W = EXPR_H = 28
VIDEO_WIDTH = 640
STRANGERS_LIMIT = 2   # 秒
SMILE_LIMIT     = 2   # 秒

id_card_to_name, id_card_to_type = fileassistant.get_people_info(people_info_path)
expr_id_to_name = fileassistant.get_facial_expression_info(expr_info_path)

ts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
print('[INFO] %s 陌生人检测+表情检测程序启动.' % ts)

if not input_video:
    vs = cv2.VideoCapture(0)
    time.sleep(2)
else:
    vs = cv2.VideoCapture(input_video)

faceutil = FaceUtil(face_recog_model)
expr_model = load_model(face_expr_model)

try:
    font = ImageFont.truetype(font_path, 28)
except:
    font = ImageFont.load_default()

strangers_timing = strangers_start = 0
smile_timing = smile_start = 0
frame_count = 0

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

while True:
    (grabbed, frame) = vs.read()
    if input_video and not grabbed:
        break
    if not input_video:
        frame = cv2.flip(frame, 1)

    frame = imutils.resize(frame, width=VIDEO_WIDTH)
    H, W = frame.shape[:2]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    face_location_list, names = faceutil.get_face_location_and_name(frame)

    # 1/4 和 3/4 竖线（用于陌生人方位判断）
    cv2.line(frame, (W // 4, 0), (W // 4, H), (0, 255, 255), 1)
    cv2.line(frame, (W * 3 // 4, 0), (W * 3 // 4, H), (0, 255, 255), 1)

    for ((left, top, right, bottom), name) in zip(face_location_list, names):
        ptype = id_card_to_type.get(name, '')
        color = {'old_people': (0, 0, 128), 'employee': (255, 0, 0),
                 'volunteer': (0, 255, 0)}.get(ptype, (0, 0, 255))
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

        # 陌生人检测
        if 'Unknown' in names:
            if strangers_timing == 0:
                strangers_timing = 1
                strangers_start = time.time()
            else:
                diff = time.time() - strangers_start
                ts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                if diff >= STRANGERS_LIMIT:
                    print('[EVENT] %s 房间 陌生人出现!!!' % ts)
                    snap = os.path.join(output_stranger, 'snapshot_%s.jpg' % time.strftime('%Y%m%d_%H%M%S'))
                    cv2.imwrite(snap, frame)
                    strangers_timing = 0
                    trigger_db_insert('陌生人出现!!!', 2, '房间')
        else:
            strangers_timing = 0

        # 表情检测（对人脸检测到的所有人运行，包括陌生人）
        roi = gray[top:bottom, left:right]
        if roi.size > 0:
            roi = cv2.resize(roi, (EXPR_W, EXPR_H))
            roi = roi.astype('float') / 255.0
            roi = img_to_array(roi)
            roi = np.expand_dims(roi, axis=0)
            (neutral, smile) = expr_model.predict(roi, verbose=0)[0]
            expr_label = 'Smile' if smile > neutral else 'Neutral'

            if expr_label == 'Smile':
                if smile_timing == 0:
                    smile_timing = 1
                    smile_start = time.time()
                else:
                    diff = time.time() - smile_start
                    ts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                    if diff >= SMILE_LIMIT:
                        if name != 'Unknown' and ptype == 'old_people':
                            old_name = id_card_to_name.get(name, name)
                            event_desc = '%s正在笑' % old_name
                            event_loc = '房间'
                            db_id = name
                            print('[EVENT] %s 房间 %s正在笑.' % (ts, event_desc))
                            snap = os.path.join(output_smile, 'snapshot_%s.jpg' % time.strftime('%Y%m%d_%H%M%S'))
                            cv2.imwrite(snap, frame)
                            smile_timing = 0
                            trigger_db_insert(event_desc, 0, event_loc, db_id)
                        else:
                            # 非老人微笑只打印日志，不写入数据库
                            print('[INFO] %s 检测到非老人微笑（不记录）' % ts)
        else:
            expr_label = ''
            smile_timing = 0

        # 中文标注
        display_name = id_card_to_name.get(name, name)
        if expr_label:
            display_name += ': ' + expr_label
        img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        ImageDraw.Draw(img_pil).text((left, max(0, top - 32)), display_name,
                                     font=font, fill=(255, 0, 0))
        frame = cv2.cvtColor(np.asarray(img_pil), cv2.COLOR_RGB2BGR)

    if use_gui:
        cv2.imshow('Strangers & Expression', frame)
        if cv2.waitKey(1) & 0xff == 27:
            break

    frame_count += 1
    if frame_count >= 300:
        break

vs.release()
if use_gui:
    cv2.destroyAllWindows()
print('[INFO] 处理完成，共 %d 帧' % frame_count)
