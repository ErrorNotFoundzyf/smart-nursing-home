# -*- coding: utf-8 -*-
'''
每当有人员变化时（如增加了一位老人，如删了了一位工作人员），调用该程序。
'''

from oldcare.utils import fileassistant
from imutils import paths
from oldcare.facial import FaceUtil
import os


# 全局变量
output_encoding_file_path = '../models/face_recognition_hog.pickle'
output_people_info_path = '../info/people_info.csv'
dataset_path = '../images/faces'

# get people info
print('[INFO] 获取人员信息...')
fileassistant.generate_people_info(output_people_info_path)

# re-train face recognition model
print('[INFO] 重新训练人脸识别模型...')
# grab the paths to the input images in our dataset
image_paths_old_people = list(paths.list_images(os.path.join(dataset_path,
                                                             'old_people')))
image_paths_volunteers = list(paths.list_images(os.path.join(dataset_path,
                                                             'volunteers')))
image_paths_employees = list(paths.list_images(os.path.join(dataset_path,
                                                            'employees')))

image_paths = image_paths_old_people + image_paths_volunteers + image_paths_employees

if len(image_paths) == 0:
    print('[ERROR] no images to train.')
else:
    faceutil = FaceUtil()
    print("[INFO] training face embeddings...")
    faceutil.save_embeddings(image_paths, output_encoding_file_path)
