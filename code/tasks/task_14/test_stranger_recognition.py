# -*- coding: utf-8 -*-
'''
任务14：陌生人识别-功能测试（单元测试）

使用 IoU 匹配预测框与标注框，评估陌生人识别准确率。
方法同任务6（功能测试），关键指标 >= 90%
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
TEST_CSV = os.path.join(BASE_DIR, '..', 'task_13', 'test_annotations.csv')
FRAMES_DIR = os.path.join(BASE_DIR, '..', 'task_13', 'test_frames')

def calc_iou(boxA, boxB):
    """计算两个矩形框的 IoU"""
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])
    inter = max(0, xB - xA) * max(0, yB - yA)
    areaA = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    areaB = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
    return inter / (areaA + areaB - inter) if (areaA + areaB - inter) > 0 else 0

print('[INFO] 加载人脸识别模型...')
faceutil = FaceUtil(MODEL_PATH)
faceutil.detection_method = 'hog'

# 读取标注
samples = []
with open(TEST_CSV, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        samples.append(row)

print('[INFO] 共 %d 个标注人脸\n' % len(samples))

from collections import defaultdict
frames = defaultdict(list)
for s in samples:
    frames[s['frame_file']].append(s)

IOU_THRESHOLD = 0.3  # 预测框与标注框 IoU > 0.3 算匹配

correct = 0
total = 0
known_correct = 0
known_total = 0
stranger_correct = 0
stranger_total = 0

for frame_file, gt_faces in sorted(frames.items()):
    frame_path = os.path.join(FRAMES_DIR, frame_file)
    img = cv2.imread(frame_path)
    if img is None:
        continue

    # 模型预测
    pred_locations, pred_names = faceutil.get_face_location_and_name(img)
    pred_boxes = []
    for (left, top, right, bottom), name in zip(pred_locations, pred_names):
        label = 'stranger' if name == 'Unknown' else 'known'
        pred_boxes.append((left, top, right, bottom, label, name))

    for gt in gt_faces:
        total += 1
        gt_box = (int(gt['left']), int(gt['top']), int(gt['right']), int(gt['bottom']))
        gt_label = gt['label']
        gt_name = gt['name']

        best_iou = 0
        best_match = None
        for pb in pred_boxes:
            iou = calc_iou(gt_box, pb[:4])
            if iou > best_iou:
                best_iou = iou
                best_match = pb

        if best_iou >= IOU_THRESHOLD and best_match[4] == gt_label:
            # 对已知人脸还要检查姓名是否匹配
            if gt_label == 'known':
                if best_match[5] == gt_name:
                    correct += 1
                    known_correct += 1
                else:
                    print('  ❌ %s: 姓名不匹配 (标注=%s, 预测=%s)' % (
                        frame_file, gt_name, best_match[5]))
            else:
                correct += 1
                stranger_correct += 1
        else:
            reason = 'IoU=%.2f<%.2f' % (best_iou, IOU_THRESHOLD)
            if best_iou >= IOU_THRESHOLD:
                reason = '标签不匹配(标注=%s, 预测=%s)' % (gt_label, best_match[4])
            print('  ❌ %s: %s' % (frame_file, reason))

        if gt_label == 'known':
            known_total += 1
        else:
            stranger_total += 1

print()
print('=' * 50)
print('        陌生人识别单元测试报告')
print('=' * 50)
accuracy = correct / total * 100 if total > 0 else 0
print('  总样本:     %d' % total)
print('  正确:       %d' % correct)
print('  准确率:     %.2f%%' % accuracy)
print()
known_acc = known_correct / known_total * 100 if known_total > 0 else 0
stranger_acc = stranger_correct / stranger_total * 100 if stranger_total > 0 else 0
print('  熟人识别准确率:   %d/%d = %.2f%%' % (known_correct, known_total, known_acc))
print('  陌生人识别准确率: %d/%d = %.2f%%' % (stranger_correct, stranger_total, stranger_acc))
print()

if accuracy >= 90:
    print('  ✅ 测试通过！陌生人识别准确率 >= 90%%')
else:
    print('  ❌ 测试未通过！准确率 %.2f%% < 90%%' % accuracy)
print('=' * 50)
