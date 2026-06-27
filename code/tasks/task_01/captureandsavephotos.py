
# -*- coding: utf-8 -*-
'''
使用Web摄像头 (USB摄像头)捕捉图像并保存
'''

import cv2
import time
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
video_path = os.path.join(BASE_DIR, 'test.mp4')
# video_path = ''
use_gui = os.environ.get('DISPLAY') is not None  # 检测是否有图形界面

if video_path:
    cap = cv2.VideoCapture(video_path)
else:
    cap = cv2.VideoCapture(0)

# 设置视频宽度和高度
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
time.sleep(2)

images_dir = os.path.join(BASE_DIR, 'images')
os.makedirs(images_dir, exist_ok=True)

for i in range(100):  # 拍100张图片就结束
    ret, img = cap.read()
    if not ret:
        print("读取画面失败，视频可能已结束")
        break
    if use_gui:
        cv2.imshow('img', img)
    out_path = os.path.join(images_dir, '%d.jpg' % i)
    cv2.imwrite(out_path, img)
    print(f"已保存: {out_path}")

    if use_gui:
        # 按 'ESC' 键退出
        k = cv2.waitKey(100) & 0xff
        if k == 27:
            break

# 关闭资源
cap.release()
if use_gui:
    cv2.destroyAllWindows()
print("任务1完成，共保存 %d 张图片" % (i + 1))