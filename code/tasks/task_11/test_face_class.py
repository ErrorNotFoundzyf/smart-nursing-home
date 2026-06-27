#!/usr/bin/env python
# coding: utf-8
'''
表情识别批量评估
遍历数据集图片，与目录名（ground truth）对比，输出分类报告
'''

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CODE_DIR = os.path.dirname(os.path.dirname(BASE_DIR))
if CODE_DIR not in sys.path:
    sys.path.insert(0, CODE_DIR)

OLD_CARE_HOME = os.path.dirname(CODE_DIR)

from keras.preprocessing.image import img_to_array
from keras.models import load_model
from oldcare.facial import FaceUtil
import numpy as np
from imutils import paths
import cv2
from sklearn.metrics import classification_report

# 使用共享模型
model_path = os.path.join(OLD_CARE_HOME, 'models', 'face_expression.hdf5')
dataset = os.path.join(BASE_DIR, 'dataset')

FACIAL_EXPRESSION_TARGET_WIDTH = 28
FACIAL_EXPRESSION_TARGET_HEIGHT = 28

imagePaths = sorted(list(paths.list_images(dataset)))
print('[INFO] 加载模型...')
model = load_model(model_path)
# 使用 CNN 提升人脸检测精度
faceutil = FaceUtil()
faceutil.detection_method = 'cnn'

preds = []
labels = []
missed = 0

print('[INFO] 共 %d 张测试图片，开始批量评估...' % len(imagePaths))
for i, path in enumerate(imagePaths):
    if (i + 1) % 20 == 0:
        print('  已处理 %d/%d' % (i + 1, len(imagePaths)))

    img = cv2.imread(path)
    if img is None:
        continue

    face_location = faceutil.get_face_location(img)
    if face_location:
        left, top, right, bottom = face_location[0]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        roi = gray[top:bottom, left:right]
        roi = cv2.resize(roi, (FACIAL_EXPRESSION_TARGET_WIDTH,
                               FACIAL_EXPRESSION_TARGET_HEIGHT))
        roi = roi.astype("float") / 255.0
        roi = img_to_array(roi)
        roi = np.expand_dims(roi, axis=0)

        (neutral, smile) = model.predict(roi, verbose=0)[0]
        pred = 0 if neutral > smile else 1
        preds.append(pred)
        label = 0 if 'neutral' in path.split(os.sep)[-2].lower() else 1
        labels.append(label)
    else:
        missed += 1

print()
print('===== 评估结果 =====')
print(classification_report(labels, preds, target_names=('neutral', 'smile')))
print('未检测到人脸的图片: %d / %d' % (missed, len(imagePaths)))
