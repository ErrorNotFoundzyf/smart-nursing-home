# -*- coding: utf-8 -*-
"""演示用：从表情数据集读取微笑图片，批量测试并写入数据库"""
import os, sys, time, subprocess, cv2, numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
OLD_CARE_HOME = os.path.dirname(BASE_DIR)

model_path = os.path.join(OLD_CARE_HOME, 'models', 'face_expression.hdf5')
inserting_script = os.path.join(BASE_DIR, 'tasks', 'task_22', 'inserting.py')
allow_file = os.path.join(BASE_DIR, 'tasks', 'task_22', 'allowinsertdatabase.txt')
smile_dir = os.path.join(OLD_CARE_HOME, 'images', 'face_expression', 'smile')
people_csv = os.path.join(OLD_CARE_HOME, 'info', 'people_info.csv')

# 从CSV读取老人ID和姓名
old_people_ids = []
old_people_names = []
with open(people_csv, 'r') as f:
    for line in f:
        parts = line.strip().split(',')
        if len(parts) >= 3 and parts[2] == 'old_people':
            old_people_ids.append(parts[0])
            old_people_names.append(parts[1])
id2name = dict(zip(old_people_ids, old_people_names))

print('[INFO] 加载表情识别模型...')
model = load_model(model_path)
print('[INFO] 批量测试微笑图片（将写入数据库用于演示）...')
count = 0
for fname in sorted(os.listdir(smile_dir)):
    img = cv2.imread(os.path.join(smile_dir, fname), cv2.IMREAD_GRAYSCALE)
    if img is None: continue
    roi = cv2.resize(img, (28, 28)).astype('float') / 255.0
    roi = img_to_array(roi)
    roi = np.expand_dims(roi, axis=0)
    neutral, smile = tuple(model.predict(roi, verbose=0)[0])
    if smile > neutral:
        pid = np.random.choice(old_people_ids)
        pname = id2name[pid]
        with open(allow_file, 'w') as f:
            f.write('is_allowed=1')
        subprocess.Popen([sys.executable, inserting_script,
               '--event_desc', '%s正在笑' % pname,
               '--event_type', '0',
               '--event_location', '房间',
               '--old_people_id', pid])
        count += 1
        if count <= 5:
            print('  [EVENT] %s 微笑检测成功' % pname)
        time.sleep(0.3)
    if count >= 30:
        break

print('[INFO] 已完成 %d 条微笑事件写入，请刷新Web数据管理页面' % count)
