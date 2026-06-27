# -*- coding: utf-8 -*-

'''
训练人脸识别模型

用法：
python trainingfacerecognition.py
'''


# import the necessary packages
from imutils import paths
from oldcare.facial import FaceUtil
import os

# global variable
dataset_path = '/root/Desktop/old_care_system/images/faces'
output_encoding_file_path = '/root/Desktop/old_care_system/models/face_recognition_hog.pickle'

# grab the paths to the input images in our dataset
print("[INFO] quantifying faces...")
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
