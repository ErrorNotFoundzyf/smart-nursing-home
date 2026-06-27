# -*- coding: utf-8 -*-
'''
训练人脸识别模型
用法：python3 tasks/task_12/trainingfacerecognition.py
'''

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CODE_DIR = os.path.dirname(os.path.dirname(BASE_DIR))
if CODE_DIR not in sys.path:
    sys.path.insert(0, CODE_DIR)

OLD_CARE_HOME = os.path.dirname(CODE_DIR)

from imutils import paths
from oldcare.facial import FaceUtil

# 训练数据：共享的 faces 目录
dataset_path = os.path.join(OLD_CARE_HOME, 'images', 'faces')
# 模型保存路径（覆盖原预训练模型）
output_encoding_file_path = os.path.join(
    OLD_CARE_HOME, 'models', 'face_recognition_hog.pickle')

print("[INFO] 数据集路径:", dataset_path)
print("[INFO] 模型输出路径:", output_encoding_file_path)

image_paths = list(paths.list_images(dataset_path))
print("[INFO] 共 %d 张训练图片" % len(image_paths))

if len(image_paths) == 0:
    print('[ERROR] 没有找到训练图片')
else:
    faceutil = FaceUtil()
    faceutil.detection_method = 'hog'
    print("[INFO] 开始训练人脸特征编码...")
    faceutil.save_embeddings(image_paths, output_encoding_file_path)
    print("[INFO] 训练完成，模型已保存至: %s" % output_encoding_file_path)
