# -*- coding: utf-8 -*-
'''
任务19：禁止区域入侵检测

使用 MobileNet-SSD 做人物检测 + CentroidTracker 做目标追踪，
当检测到有人越过中线（入侵禁止区域）时，保存快照并报警。

用法：python3 tasks/task_19/checkingfence.py
      python3 tasks/task_19/checkingfence.py --filename yard_01.mp4
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

from oldcare.track import CentroidTracker, TrackableObject
from imutils.video import FPS
import numpy as np
import imutils
import dlib
import cv2

use_gui = os.environ.get('DISPLAY') is not None

ap = argparse.ArgumentParser()
ap.add_argument("-f", "--filename", default='', help="测试视频文件名")
args = vars(ap.parse_args())

prototxt_path  = os.path.join(OLD_CARE_HOME, 'models', 'mobilenet_ssd', 'MobileNetSSD_deploy.prototxt')
model_path     = os.path.join(OLD_CARE_HOME, 'models', 'mobilenet_ssd', 'MobileNetSSD_deploy.caffemodel')
snapshot_dir   = os.path.join(BASE_DIR, 'supervision', 'fence')
os.makedirs(snapshot_dir, exist_ok=True)

# Database insertion integration
task_22_dir = os.path.join(CODE_DIR, 'tasks', 'task_22')
inserting_script = os.path.join(task_22_dir, 'inserting.py')
allow_file = os.path.join(task_22_dir, 'allowinsertdatabase.txt')

def trigger_db_insert(event_desc, event_type, event_location):
    with open(allow_file, 'w') as f:
        f.write('is_allowed=1')
    cmd = [sys.executable, inserting_script,
           '--event_desc', event_desc,
           '--event_type', str(event_type),
           '--event_location', event_location]
    subprocess.Popen(cmd)

input_video = args['filename']
if input_video and not os.path.isabs(input_video):
    input_video = os.path.join(OLD_CARE_HOME, 'images', 'tests', 'videos', input_video)

CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair",
           "cow", "diningtable", "dog", "horse", "motorbike",
           "person", "pottedplant", "sheep", "sofa", "train", "tvmonitor"]

MINIMUM_CONFIDENCE = 0.80
SKIP_FRAMES = 30

current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
print('[INFO] %s 禁止区域检测程序启动.' % current_time)

print('[INFO] 加载 MobileNet-SSD 模型...')
net = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)

if not input_video:
    vs = cv2.VideoCapture(0)
    time.sleep(2)
else:
    print('[INFO] 打开视频: %s' % input_video)
    vs = cv2.VideoCapture(input_video)

W = H = None
ct = CentroidTracker(maxDisappeared=40, maxDistance=50)
trackers = []
trackableObjects = {}
totalFrames = totalDown = totalUp = intrusion_count = 0

fps = FPS().start()

while True:
    ret, frame = vs.read()
    if input_video and not ret:
        break
    if not input_video:
        frame = cv2.flip(frame, 1)

    frame = imutils.resize(frame, width=500)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    if W is None or H is None:
        (H, W) = frame.shape[:2]

    status = "Waiting"
    rects = []

    if totalFrames % SKIP_FRAMES == 0:
        status = "Detecting"
        trackers = []
        blob = cv2.dnn.blobFromImage(frame, 0.007843, (W, H), 127.5)
        net.setInput(blob)
        detections = net.forward()

        for i in np.arange(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > MINIMUM_CONFIDENCE:
                idx = int(detections[0, 0, i, 1])
                if CLASSES[idx] != "person":
                    continue
                box = detections[0, 0, i, 3:7] * np.array([W, H, W, H])
                (startX, startY, endX, endY) = box.astype("int")
                tracker = dlib.correlation_tracker()
                tracker.start_track(rgb, dlib.rectangle(startX, startY, endX, endY))
                trackers.append(tracker)
    else:
        for tracker in trackers:
            status = "Tracking"
            tracker.update(rgb)
            pos = tracker.get_position()
            startX, startY = int(pos.left()), int(pos.top())
            endX, endY = int(pos.right()), int(pos.bottom())
            cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2)
            rects.append((startX, startY, endX, endY))

    # 禁止区域警戒线（水平中线）
    cv2.line(frame, (0, H // 2), (W, H // 2), (0, 0, 255), 2)
    cv2.putText(frame, "RESTRICTED ZONE", (10, H // 2 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    objects = ct.update(rects)

    for (objectID, centroid) in objects.items():
        to = trackableObjects.get(objectID, None)
        if to is None:
            to = TrackableObject(objectID, centroid)
        else:
            y = [c[1] for c in to.centroids]
            direction = centroid[1] - np.mean(y)
            to.centroids.append(centroid)

            if not to.counted:
                if direction < 0 and centroid[1] < H // 2:
                    totalUp += 1
                    to.counted = True
                elif direction > 0 and centroid[1] > H // 2:
                    totalDown += 1
                    to.counted = True
                    intrusion_count += 1
                    ts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                    print('[EVENT] %s 院子 有人闯入禁止区域!!!' % ts)
                    snap_name = 'snapshot_%s.jpg' % time.strftime('%Y%m%d_%H%M%S')
                    cv2.imwrite(os.path.join(snapshot_dir, snap_name), frame)
                    print('[INFO] 快照已保存: %s' % snap_name)
                    trigger_db_insert('有人闯入禁止区域!!!', 4, '院子')

        trackableObjects[objectID] = to

        cv2.putText(frame, "ID %d" % objectID, (centroid[0] - 10, centroid[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.circle(frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)

    info = [("Intrusions", intrusion_count), ("Status", status)]
    for (i, (k, v)) in enumerate(info):
        cv2.putText(frame, "%s: %s" % (k, v), (10, H - ((i * 20) + 20)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    if use_gui:
        cv2.imshow("Prohibited Area", frame)
        if cv2.waitKey(1) & 0xff == 27:
            break

    totalFrames += 1
    fps.update()

    if input_video and totalFrames >= 500:
        break

fps.stop()
vs.release()
if use_gui:
    cv2.destroyAllWindows()

print('[INFO] 处理帧数: %d' % totalFrames)
print('[INFO] 耗时: %.2f 秒, FPS: %.2f' % (fps.elapsed(), fps.fps()))
print('[INFO] 检测到入侵次数: %d' % intrusion_count)
print('[INFO] 快照保存目录: %s' % snapshot_dir)
