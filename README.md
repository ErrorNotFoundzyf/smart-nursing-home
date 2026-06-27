# 智慧养老院智能监控系统 (Smart Nursing Home Monitoring System)

## 📋 项目简介

基于计算机视觉（TensorFlow + dlib + OpenCV）的养老院智能监控系统，包含 AI 检测端和 Flask Web 管理后台。

**适用场景**：养老院老人安全监控、陌生人识别、摔倒检测、禁区入侵检测、义工互动检测等。

## 🗂️ 项目结构

```
├── code/                    # AI 检测系统核心代码
│   ├── tasks/               # 22个任务复现代码（task_01 ~ task_22）
│   ├── oldcare/             # 自定义工具库（人脸识别、模型训练、目标跟踪等）
│   ├── checking*.py         # 生产运行脚本（整合版）
│   ├── training*.py         # 模型训练脚本
│   └── inserting.py         # 数据库写入脚本
├── web_backend/             # Flask Web 管理后台
│   ├── app/                 # 应用模块（登录/老人/员工/义工/数据管理）
│   ├── config.py            # 数据库配置
│   └── runit.py             # 启动入口
├── models/                  # 预训练模型（小文件）
│   ├── face_recognition_hog.pickle   # 人脸识别模型 (342KB)
│   └── mobilenet_ssd/                # MobileNet-SSD 配置文件
├── info/                    # 人员信息 CSV
├── audios/                  # 语音提示文件
└── .gitignore               # Git 忽略规则
```

## 🚀 快速开始

### 环境要求

| 组件 | 版本 |
|------|------|
| Ubuntu | 20.04+ |
| Python | 3.8 / 3.9 |
| TensorFlow | 2.8 |
| Keras | 2.8 |
| MySQL | 8.0 |
| Redis | (Flask-SocketIO 所需) |

### 安装步骤

```bash
# 1. 创建 conda 环境
conda create -n tensorflow python=3.8
conda activate tensorflow

# 2. 安装依赖
pip install tensorflow==2.8 keras==2.8 opencv-python dlib face_recognition
pip install imutils scikit-learn scipy pillow pandas
pip install flask flask-sqlalchemy flask-socketio flask-login
pip install mysql-connector-python eventlet

# 3. 配置 MySQL 数据库
mysql -u root -p < sql/old_care.sql

# 4. 启动服务
sudo service mysql start
sudo service redis start

# 5. 启动 Web 后台
cd web_backend
python runit.py &

# 6. 运行 AI 检测（测试视频）
cd ../code
python checkingfalldetection.py --filename corridor_01.avi  # 摔倒检测
python checkingfence.py --filename yard_01.mp4              # 禁区入侵检测
python checkingstrangersandfacialexpression.py --filename room_01.mp4  # 陌生人+表情
python checkingvolunteeractivity.py --filename desk_01.mp4   # 义工互动检测
```

## 📦 模型文件说明

大模型文件因 GitHub 大小限制未包含，需手动下载或训练：

| 模型文件 | 大小 | 获取方式 |
|----------|------|----------|
| `models/fall_detection.hdf5` | 65MB | [下载](https://...) 或运行 `code/tasks/task_16/trainingfalldetection.py` 训练 |
| `models/face_expression.hdf5` | 13MB | [下载](https://...) 或运行 `code/tasks/task_09/train.py` 训练 |
| `models/mobilenet_ssd/MobileNetSSD_deploy.caffemodel` | 23MB | [下载](https://github.com/chuanqi305/MobileNet-SSD) |
| `code/tasks/task_16/points_det/pose/coco/pose_iter_440000.caffemodel` | 200MB | [OpenPose COCO 模型](http://posefs1.perception.cs.cmu.edu/OpenPose/models/pose/coco/pose_iter_440000.caffemodel) |

## ✅ 任务清单

### 计算机视觉 (22/22)
- 任务1-6: 人脸检测（USB摄像头/dlib/Haarv/MTCNN/评估）
- 任务7: 人脸图像采集（7种动作语音引导）
- 任务8-11: 表情识别（训练/测试/评估）
- 任务12-14: 陌生人识别（训练/数据/评估）
- 任务15-18: 摔倒检测（CNN + OpenPose 骨架）
- 任务19: 禁止区域入侵检测
- 任务20: 老人义工互动检测
- 任务21: 摄像头实时显示
- 任务22: 代码整合

### Web 端 (15/15)
- 管理员登录/密码管理
- 老人/员工/义工 增删改查、头像管理、报表统计
- 数据管理实时事件展示

## 📐 架构图

```
摄像头 → [AI检测] → checking*.py  → inserting.py → MySQL → Flask Web → 浏览器
                            ↕                           ↕
                     TensorFlow/dlib/OpenCV      Flask-SQLAlchemy/SocketIO
```
