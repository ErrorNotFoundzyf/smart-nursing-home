# -*- coding: utf-8 -*-
'''
训练摔倒检测模型（MiniVGGNet，二分类：fall / normal）
用法：python3 tasks/task_16/trainingfalldetection.py
'''

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CODE_DIR = os.path.dirname(os.path.dirname(BASE_DIR))
if CODE_DIR not in sys.path:
    sys.path.insert(0, CODE_DIR)

OLD_CARE_HOME = os.path.dirname(CODE_DIR)

from oldcare.datasets import SimpleDatasetLoader
from oldcare.preprocessing import AspectAwarePreprocessor
from oldcare.preprocessing import ImageToArrayPreprocessor
from oldcare.conv import MiniVGGNet
from oldcare.callbacks import TrainingMonitor
from imutils import paths
from sklearn.model_selection import train_test_split
from tensorflow.keras.optimizers import SGD
from sklearn.metrics import classification_report
from tensorflow.keras.utils import to_categorical
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# 全局变量
dataset_path = os.path.join(OLD_CARE_HOME, 'images', 'fall_collecting', 'dataset')
output_model_path = os.path.join(OLD_CARE_HOME, 'models', 'fall_detection.hdf5')
output_plot_path = os.path.join(OLD_CARE_HOME, 'plots', 'fall_detection.png')

# 全局常量
TARGET_WIDTH = 64
TARGET_HEIGHT = 64
BATCH_SIZE = 32
EPOCHS = 10
LR_INIT = 0.01
DECAY = LR_INIT / EPOCHS
MOMENTUM = 0.9

# 加载图片
aap = AspectAwarePreprocessor(TARGET_WIDTH, TARGET_HEIGHT)
iap = ImageToArrayPreprocessor()

print("[INFO] loading images from %s..." % dataset_path)
imagePaths = list(paths.list_images(dataset_path))
print("[INFO] 共 %d 张图片" % len(imagePaths))

sdl = SimpleDatasetLoader(preprocessors=[aap, iap])
(data, labels) = sdl.load(imagePaths, 500, False)
data = data.astype("float") / 255.0

# 标签 one-hot 编码
le = LabelEncoder().fit(labels)
labels = to_categorical(le.transform(labels), 2)

# 80% 训练 / 20% 测试
(trainX, testX, trainY, testY) = train_test_split(
    data, labels, test_size=0.20, stratify=labels, random_state=42)

# 数据增强
aug = ImageDataGenerator(rotation_range=30, width_shift_range=0.1,
                         height_shift_range=0.1, shear_range=0.2,
                         zoom_range=0.2, horizontal_flip=True,
                         fill_mode="nearest")

# 构建模型
print("[INFO] compiling model...")
model = MiniVGGNet.build(width=TARGET_WIDTH, height=TARGET_HEIGHT,
                         depth=3, classes=2)
opt = SGD(learning_rate=LR_INIT, decay=DECAY, momentum=MOMENTUM, nesterov=True)
model.compile(loss="binary_crossentropy", optimizer=opt, metrics=["accuracy"])

# 回调
callbacks = [TrainingMonitor(output_plot_path)]

# 训练
print("[INFO] training network...")
H = model.fit(aug.flow(trainX, trainY, batch_size=BATCH_SIZE),
              validation_data=(testX, testY),
              steps_per_epoch=len(trainX) // BATCH_SIZE,
              epochs=EPOCHS,
              callbacks=callbacks, verbose=1)

# 评估
print("[INFO] evaluating network...")
predictions = model.predict(testX, batch_size=BATCH_SIZE)
print(classification_report(testY.argmax(axis=1), predictions.argmax(axis=1),
                            target_names=le.classes_))

# 保存模型
print("[INFO] serializing network to %s ..." % output_model_path)
model.save(output_model_path)
print("[INFO] 训练完成！")
