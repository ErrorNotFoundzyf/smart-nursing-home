import cv2
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 切换到脚本所在目录，确保相对导入正常工作
os.chdir(BASE_DIR)
sys.path.insert(0, BASE_DIR)

from model.mtcnn import mtcnn
from qstutils.computervision import utils

output_dir = os.path.join(BASE_DIR, 'detected_faces')
os.makedirs(output_dir, exist_ok=True)

# 初始化MTCNN模型
model = mtcnn()
threshold = [0.5, 0.6, 0.7]  # PNet/RNet/ONet 分类概率阈值

# 检测多张图片
image_files = ['img/dataset1.png', 'img/dataset2.png']

for filename in image_files:
    img_path = os.path.join(BASE_DIR, filename)
    if not os.path.exists(img_path):
        print(f"图片不存在: {img_path}")
        continue

    img = cv2.imread(img_path)
    if img is None:
        print(f"无法读取图片: {img_path}")
        continue

    print(f"正在检测: {filename}")
    rectangles = model.detectFace(img, threshold)

    draw = img.copy()
    for rect in rectangles:
        if rect is not None:
            x1, y1, x2, y2 = int(rect[0]), int(rect[1]), int(rect[2]), int(rect[3])
            cv2.rectangle(draw, (x1, y1), (x2, y2), (0, 0, 255), 2)

    out_path = os.path.join(output_dir, os.path.basename(filename))
    cv2.imwrite(out_path, draw)
    print(f"  检测到 {len(rectangles)} 张人脸，结果已保存: {out_path}")
    for i, rect in enumerate(rectangles):
        if rect is not None:
            print(f"    人脸{i+1}: ({int(rect[0])},{int(rect[1])}) - ({int(rect[2])},{int(rect[3])})")

print("任务4完成")
