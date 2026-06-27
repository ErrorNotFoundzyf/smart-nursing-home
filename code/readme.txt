oldcare是包，包含了所有代码的辅助包
adafruit是目录，包含了舵机的依赖包
templates是目录，存放html文件
readme.txt用于说明文档
剩下的.py文件全是主程序

主程序介绍：
collectingfaces.py 采集人脸数据

trainingfacerecognition.py 训练人脸识别模型
testingfacerecognition.py 测试人脸识别模型

trainingfacialexpression.py 训练表情识别模型
testingfacialexpression.py 测试表情识别模型

startingcameraservice.py 开启摄像头服务
startingrecording.py 为摄像头录像

trainingfalldetection.py 训练摔倒检测模型
testingfalldetection.py 测试摔倒检测模型

testingvolunteeractivity.py 测试义工老人互动
checkingvolunteeractivity.py 检测义工老人互动主程序

testingfence.py 测试禁止区域入侵检测

checkingfalldetection.py 摔倒检测主程序

checkingfence.py 禁止区域检测主程序

checkingstrangersandfacialexpression.py 陌生人和表情识别主程序

insertingcontrol.py 控制插入数据库的控制程序
inserting.py 插入数据库主数据
allowinsertdatabase.txt 插入数据库的控制文件

insertingnewpeople.py 每当有人员变化调用此方法