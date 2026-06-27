import face_recognition
import cv2
import os
import xml.dom.minidom

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

dataset = 'facil_dataset'
imagePaths = sorted([os.path.join(dataset, f) for f in os.listdir(dataset) if f.endswith('.jpg')])

detection_method = 'cnn'  # HOG 准确率不足，改用 CNN 提升精度


def get_face_location(image):
    """人脸检测，返回 (left, top, right, bottom) 格式的坐标列表"""
    face_location_list = []
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    face_locations = face_recognition.face_locations(
        gray, number_of_times_to_upsample=1, model=detection_method
    )
    for (top, right, bottom, left) in face_locations:
        face_location_list.append((left, top, right, bottom))
    return face_location_list


correct = 0
total_images = len(imagePaths)

for i, path in enumerate(imagePaths):
    print('正在处理第%d张图像: %s' % (i + 1, os.path.basename(path)))

    img = cv2.imread(path)
    if img is None:
        print('  无法读取图片，跳过')
        continue

    # 获取检测到的人脸框
    face_location_list = get_face_location(img)

    # 获取对应的xml标注文件
    xml_p = path.replace('.jpg', '.xml')
    if not os.path.exists(xml_p):
        print('  标注文件不存在: %s，跳过' % xml_p)
        continue

    document_tree = xml.dom.minidom.parse(xml_p)
    bndbox = document_tree.getElementsByTagName("bndbox")

    # 解析真实人脸框坐标
    gt_location_list = []
    for box in bndbox:
        xmin = box.getElementsByTagName("xmin")[0].childNodes[0].data
        ymin = box.getElementsByTagName("ymin")[0].childNodes[0].data
        xmax = box.getElementsByTagName("xmax")[0].childNodes[0].data
        ymax = box.getElementsByTagName("ymax")[0].childNodes[0].data
        gt_location_list.append([xmin, ymin, xmax, ymax])

    pred_count = len(face_location_list)
    gt_count = len(gt_location_list)

    if gt_count == pred_count:
        auc = 0
        for gt in gt_location_list:
            for pred in face_location_list:
                gt_xmin, gt_ymin, gt_xmax, gt_ymax = map(int, gt)
                pre_xmin, pre_ymin, pre_xmax, pre_ymax = map(int, pred)

                # 计算 IoU
                area1 = (gt_xmax - gt_xmin) * (gt_ymax - gt_ymin)
                area2 = (pre_xmax - pre_xmin) * (pre_ymax - pre_ymin)

                lt_x = max(gt_xmin, pre_xmin)
                lt_y = max(gt_ymin, pre_ymin)
                rd_x = min(gt_xmax, pre_xmax)
                rd_y = min(gt_ymax, pre_ymax)

                inter = max(0, rd_x - lt_x) * max(0, rd_y - lt_y)
                iou = inter / (area1 + area2 - inter) if (area1 + area2 - inter) > 0 else 0

                if iou > 0.5:
                    auc += 1

        if auc >= gt_count:
            correct += 1
        else:
            print('  预测框与标注不完全匹配 (IoU > 0.5 的 %d/%d)' % (auc, gt_count))
    else:
        print('  预测框(%d)与标注(%d)数目不一致' % (pred_count, gt_count))

print('\n===== 检测结果 =====')
print('总图片数: %d' % total_images)
print('正确检测: %d' % correct)
print('人脸检测准确率: %.2f%%' % (correct / total_images * 100))
