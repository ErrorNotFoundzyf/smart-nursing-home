import cv2
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(BASE_DIR, 'detected_faces')
os.makedirs(output_dir, exist_ok=True)

# 加载Haar级联分类器
cascade_path = os.path.join(BASE_DIR, 'haarcascade_frontalface_default.xml')
face_cascade = cv2.CascadeClassifier(cascade_path)

# 检测多张图片
image_files = ['dataset1.png', 'dataset2.png']

for filename in image_files:
    img_path = os.path.join(BASE_DIR, filename)
    if not os.path.exists(img_path):
        print(f"图片不存在: {img_path}")
        continue

    img = cv2.imread(img_path)
    if img is None:
        print(f"无法读取图片: {img_path}")
        continue

    # 转为灰度图像
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 人脸检测
    # scaleFactor: 每次迭代时图像的压缩率
    # minNeighbors: 每个人脸矩形保留近似数目的最小值
    faces = face_cascade.detectMultiScale(
        image=gray_img, scaleFactor=1.3, minNeighbors=5
    )

    print(f"{filename}: 检测到 {len(faces)} 张人脸")
    for i, (x, y, w, h) in enumerate(faces):
        print(f"  人脸{i+1}: (x={x}, y={y}, w={w}, h={h})")
        img = cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

    # 保存检测结果
    out_path = os.path.join(output_dir, f'detected_{filename}')
    cv2.imwrite(out_path, img)
    print(f"  结果已保存: {out_path}")
    print()

print("任务3完成")
