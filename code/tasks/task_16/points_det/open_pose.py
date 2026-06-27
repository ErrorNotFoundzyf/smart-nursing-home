#!/usr/bin/env python
# coding: utf-8
'''
OpenPose 人体姿态估计 + 摔倒检测

通过检测人体关键点（肩膀、臀部等），计算躯干倾斜角度
判断是否摔倒。若斜率 < 0.58 则判定为摔倒。

用法：python3 tasks/task_16/points_det/open_pose.py
      python3 tasks/task_16/points_det/open_pose.py --image tests/pose01.jpg
'''

import cv2
import numpy as np
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
use_gui = os.environ.get('DISPLAY') is not None

MODE = "COCO"

if MODE == "COCO":
    protoFile = os.path.join(BASE_DIR, "pose/coco/pose_deploy_linevec.prototxt")
    weightsFile = os.path.join(BASE_DIR, "pose/coco/pose_iter_440000.caffemodel")
    nPoints = 18
    POSE_PAIRS = [[1, 0], [1, 2], [1, 5], [2, 3], [3, 4],
                  [5, 6], [6, 7], [1, 8], [8, 9], [9, 10],
                  [1, 11], [11, 12], [12, 13], [0, 14], [0, 15],
                  [14, 16], [15, 17]]
elif MODE == "MPI":
    protoFile = os.path.join(BASE_DIR, "pose/mpi/pose_deploy_linevec.prototxt")
    weightsFile = os.path.join(BASE_DIR, "pose/mpi/pose_iter_160000.caffemodel")
    nPoints = 15
    POSE_PAIRS = [[0, 1], [1, 2], [2, 3], [3, 4], [1, 5],
                  [5, 6], [6, 7], [1, 14], [14, 8], [8, 9],
                  [9, 10], [14, 11], [11, 12], [12, 13]]

import argparse
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", default="tests/pose03.jpg", help="输入图片")
args = vars(ap.parse_args())
image_path = os.path.join(BASE_DIR, args['image'])

if not os.path.exists(weightsFile):
    print("[ERROR] 模型文件不存在: %s" % weightsFile)
    print("请下载 pose_iter_440000.caffemodel (~200MB)")
    exit(1)

print("[INFO] 加载 OpenPose 模型...")
net = cv2.dnn.readNetFromCaffe(protoFile, weightsFile)

inWidth = 368
inHeight = 368

frame = cv2.imread(image_path)
if frame is None:
    print("[ERROR] 无法读取图片: %s" % image_path)
    exit(1)

print("[INFO] 检测图片: %s" % image_path)
frameCopy = np.copy(frame)
frameWidth = frame.shape[1]
frameHeight = frame.shape[0]
threshold = 0.1

inpBlob = cv2.dnn.blobFromImage(frame, 1.0 / 255, (inWidth, inHeight),
                                (0, 0, 0), swapRB=False, crop=False)
net.setInput(inpBlob)
output = net.forward()

H = output.shape[2]
W = output.shape[3]

points = []
for i in range(nPoints):
    probMap = output[0, i, :, :]
    minVal, prob, minLoc, point = cv2.minMaxLoc(probMap)
    x = (frameWidth * point[0]) / W
    y = (frameHeight * point[1]) / H

    if prob > threshold:
        cv2.circle(frameCopy, (int(x), int(y)), 8, (0, 255, 255), thickness=-1, lineType=cv2.FILLED)
        cv2.putText(frameCopy, "{}".format(i), (int(x), int(y)),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, lineType=cv2.LINE_AA)
        cv2.circle(frame, (int(x), int(y)), 8, (0, 0, 255), thickness=-1, lineType=cv2.FILLED)
        points.append((int(x), int(y)))
    else:
        points.append(None)

# 绘制骨架
for pair in POSE_PAIRS:
    partA, partB = pair
    if points[partA] and points[partB]:
        cv2.line(frame, points[partA], points[partB], (0, 255, 255), 3)

# 摔倒检测：计算肩膀(point 1)到臀部(point 8)的斜率
if points[1] and points[8]:
    k = abs((points[1][1] - points[8][1]) / max(points[1][0] - points[8][0], 1))
    print("[INFO] 躯干斜率: %.2f" % k)
    if k < 0.58:
        print("⚠️  警告！！！检测到有人摔倒！")
        cv2.putText(frame, "FALL DETECTED!", (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
    else:
        print("[INFO] 姿态正常")
        cv2.putText(frame, "Normal", (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
else:
    print("[WARNING] 未检测到完整的关键点，无法判断是否摔倒")

# 保存结果
output_dir = os.path.join(BASE_DIR, 'output')
os.makedirs(output_dir, exist_ok=True)
out_path = os.path.join(output_dir, 'result_%s' % os.path.basename(args['image']))
cv2.imwrite(out_path, frame)
print("[INFO] 结果已保存: %s" % out_path)

if use_gui:
    cv2.imshow('Keypoints', frameCopy)
    cv2.imshow('Skeleton', frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
