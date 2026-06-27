# -*- coding: utf-8 -*-
'''
任务22整合：摔倒检测主程序（含计时报警 + 数据库写入）

用法：python3 tasks/task_22/checkingfalldetection.py
      python3 tasks/task_22/checkingfalldetection.py --filename corridor_01.avi
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

from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
import numpy as np
import cv2

use_gui = os.environ.get('DISPLAY') is not None

ap = argparse.ArgumentParser()
ap.add_argument("-f", "--filename", default='')
args = vars(ap.parse_args())
input_video = args['filename']
if input_video and not os.path.isabs(input_video):
    input_video = os.path.join(OLD_CARE_HOME, 'images', 'tests', 'videos', input_video)

model_path      = os.path.join(OLD_CARE_HOME, 'models', 'fall_detection.hdf5')
output_fall_dir = os.path.join(OLD_CARE_HOME, 'supervision', 'fall')
allow_file      = os.path.join(BASE_DIR, 'allowinsertdatabase.txt')
inserting_script= os.path.join(BASE_DIR, 'inserting.py')
os.makedirs(output_fall_dir, exist_ok=True)

TARGET_WIDTH = TARGET_HEIGHT = 64
FALL_LIMIT_TIME = 1  # 持续摔倒超过1秒才报警

if not input_video:
    vs = cv2.VideoCapture(0)
    time.sleep(2)
else:
    vs = cv2.VideoCapture(input_video)

print('[INFO] 加载摔倒检测模型...')
model = load_model(model_path)
print('[INFO] 开始检测是否有人摔倒...')

fall_timing = 0
fall_start_time = 0
frame_count = 0

while True:
    (grabbed, image) = vs.read()
    if input_video and not grabbed:
        break
    if not input_video:
        image = cv2.flip(image, 1)

    roi = cv2.resize(image, (TARGET_WIDTH, TARGET_HEIGHT))
    roi = roi.astype('float') / 255.0
    roi = img_to_array(roi)
    roi = np.expand_dims(roi, axis=0)

    (fall, normal) = model.predict(roi, verbose=0)[0]
    label = 'Fall (%.2f)' % fall if fall > normal else 'Normal (%.2f)' % normal
    cv2.putText(image, label, (image.shape[1] - 160, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    if fall > normal:
        if fall_timing == 0:
            fall_timing = 1
            fall_start_time = time.time()
        else:
            diff = time.time() - fall_start_time
            ts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            if diff >= FALL_LIMIT_TIME:
                print('[EVENT] %s 走廊 有人摔倒!!!' % ts)
                snap = os.path.join(output_fall_dir, 'snapshot_%s.jpg' % time.strftime('%Y%m%d_%H%M%S'))
                cv2.imwrite(snap, image)
                # 重置计时，避免重复触发
                fall_timing = 0
                # 写入数据库（需Web服务运行）
                with open(allow_file, 'w') as f:
                    f.write('is_allowed=1')
                subprocess.Popen([sys.executable, inserting_script,
                                  '--event_desc', '有人摔倒!!!',
                                  '--event_type', '3',
                                  '--event_location', '走廊'])
    else:
        fall_timing = 0

    if use_gui:
        cv2.imshow('Fall Detection', image)
        if cv2.waitKey(1) & 0xff == 27:
            break

    frame_count += 1
    if frame_count >= 300:
        break

vs.release()
if use_gui:
    cv2.destroyAllWindows()
print('[INFO] 处理完成，共 %d 帧' % frame_count)
