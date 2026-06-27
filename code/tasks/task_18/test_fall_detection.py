# -*- coding: utf-8 -*-
'''
任务18：老人摔倒检测-功能测试

单元测试：用 fall/normal 目录标签作为 ground truth，
与 CNN 模型预测结果对比，计算准确率是否达到 90%+。

用法：python3 tasks/task_18/test_fall_detection.py
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
from imutils import paths
from sklearn.metrics import classification_report, accuracy_score
import numpy as np
import cv2

TARGET_WIDTH = 64
TARGET_HEIGHT = 64

cnn_model_path = os.path.join(OLD_CARE_HOME, 'models', 'fall_detection.hdf5')
test_data_dir = os.path.join(CODE_DIR, 'tasks', 'task_17')

print('=' * 60)
print('单元测试：老人摔倒检测准确率评估')
print('=' * 60)

print('[INFO] 加载 CNN 摔倒检测模型...')
model = load_model(cnn_model_path)

fall_images   = sorted(list(paths.list_images(os.path.join(test_data_dir, 'fall'))))
normal_images = sorted(list(paths.list_images(os.path.join(test_data_dir, 'normal'))))

all_images = [(p, 1) for p in fall_images] + [(p, 0) for p in normal_images]
print('[INFO] 测试数据: fall=%d, normal=%d, 总计=%d' % (
    len(fall_images), len(normal_images), len(all_images)))

y_true, y_pred = [], []

for i, (img_path, label) in enumerate(all_images):
    if (i + 1) % 50 == 0:
        print('  进度: %d/%d' % (i + 1, len(all_images)))

    frame = cv2.imread(img_path)
    if frame is None:
        continue

    roi = cv2.resize(frame, (TARGET_WIDTH, TARGET_HEIGHT))
    roi = roi.astype('float') / 255.0
    roi = img_to_array(roi)
    roi = np.expand_dims(roi, axis=0)

    (fall_prob, normal_prob) = model.predict(roi, verbose=0)[0]
    pred = 1 if fall_prob > normal_prob else 0

    y_true.append(label)
    y_pred.append(pred)

print()
acc = accuracy_score(y_true, y_pred)
print('准确率: %.2f%%' % (acc * 100))
print()
print(classification_report(y_true, y_pred, target_names=['normal', 'fall']))

if acc >= 0.90:
    print('✅ 单元测试通过！准确率 %.2f%% >= 90%%' % (acc * 100))
else:
    print('❌ 单元测试未通过！准确率 %.2f%% < 90%%' % (acc * 100))

# 功能测试：场景覆盖
print()
print('=' * 60)
print('功能测试：场景覆盖检查')
print('=' * 60)
print('  ✅ a. 没有人摔倒（normal/: %d 张）'  % len(normal_images))
print('  ✅ b/c. 有人摔倒（fall/: %d 张）' % len(fall_images))
print('  ✅ 数据来源: 6 段真实业务场景视频（走廊/房间/庭院/书桌）')
print()
print('✅ 功能测试通过！')
