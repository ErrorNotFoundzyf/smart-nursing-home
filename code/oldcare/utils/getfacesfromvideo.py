# -*- coding: utf-8 -*-

'''
从视频中把含有人脸的画面截取出来
'''

from oldcare.facial import FaceUtil
import cv2
import os

input_video = '../images/face_collecting/raw_videos/02.mp4'
output_path = '../images/face_collecting/extracted_images/02'
prefix = '01'

faceutil = FaceUtil()

vs = cv2.VideoCapture(input_video)

image_counter = 1
face_counter = 0
while True:
    # grab the current frame
    (grabbed, frame) = vs.read()
    if input_video and not grabbed:
        break
    
    face_location_list = faceutil.get_face_location(frame)
    
    for ((left, top, right, bottom)) in face_location_list:
        image_to_save = frame[top-10:bottom+50, left-10:right+10]
        if image_to_save.shape[0] < 128 + 60 or image_to_save.shape[1] < 128 + 20:
            continue
        
        face_counter += 1
        cv2.imwrite(os.path.join(output_path, '%s-%d.jpg' %(prefix, image_counter)), image_to_save)
    
    print('[INFO] processed %d images, got %d faces' %(image_counter, face_counter))
    image_counter += 1

vs.release()
cv2.destroyAllWindows()