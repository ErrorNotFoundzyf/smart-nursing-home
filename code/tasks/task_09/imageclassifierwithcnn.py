import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import BatchNormalization
from tensorflow.keras.layers import Conv2D
from tensorflow.keras.layers import MaxPooling2D
from tensorflow.keras.layers import Activation
from tensorflow.keras.layers import Flatten
from tensorflow.keras.layers import Dropout
from tensorflow.keras.layers import Dense
from tensorflow.keras import backend as K
from tensorflow.keras.utils import plot_model

class CustomNet:
   @staticmethod
   def build(width, height, depth, classes):
       # 初始化模型
       # "#默认通道在后
       model = Sequential()
       inputShape = (height, width, depth)
       chanDim = -1
       
       # 如果通道在前，我们更换输入数据通道轴的位置
       # and channels dimension
       if K.image_data_format() == "channels_first":
           inputShape = (depth, height, width)
           chanDim = 1
       
       # 第一层 CONV => RELU => CONV => RELU => POOL layer set
       model.add(Conv2D(32, (3, 3), padding="same",
           input_shape=inputShape))
       model.add(Activation("relu"))
       model.add(BatchNormalization(axis=chanDim))
       model.add(Conv2D(32, (3, 3), padding="same"))
       model.add(Activation("relu"))
       model.add(BatchNormalization(axis=chanDim))
       model.add(MaxPooling2D(pool_size=(2, 2)))
       model.add(Dropout(0.25))
       
       # 第二层 CONV => RELU => CONV => RELU => POOL layer set
       model.add(Conv2D(64, (3, 3), padding="same"))
       model.add(Activation("relu"))
       model.add(BatchNormalization(axis=chanDim))
       model.add(Conv2D(64, (3, 3), padding="same"))
       model.add(Activation("relu"))
       model.add(BatchNormalization(axis=chanDim))
       model.add(MaxPooling2D(pool_size=(2, 2)))
       model.add(Dropout(0.25))
       
       # first (and only) set of FC => RELU layers
       model.add(Flatten())
       model.add(Dense(512))
       model.add(Activation("relu"))
       model.add(BatchNormalization())
       model.add(Dropout(0.5))
       
       # softmax classifier
       model.add(Dense(classes))
       model.add(Activation("softmax"))
       
       # return the constructed network architecture
       return model


model = CustomNet.build(28,28,1,2)

plot_model(model, show_shapes=True)   #绘制网络结构图
model.summary()
TARGET_WIDTH = 28
TARGET_HEIGHT = 28
BATCH_SIZE = 64
EPOCHS = 15
LR_INIT = 0.1
DECAY = LR_INIT/EPOCHS
MOMENTUM = 0.6

dataset_path = 'images'
output_model_path = 'models/face_expression.hdf5'
output_plot_path = 'plots/face_expression.png'
from oldcare.preprocessing import AspectAwarePreprocessor
aap = AspectAwarePreprocessor(TARGET_WIDTH, TARGET_HEIGHT)
from oldcare.preprocessing import ImageToArrayPreprocessor
iap = ImageToArrayPreprocessor()
print("[INFO] loading images...")
from imutils import paths
imagePaths = list(paths.list_images(dataset_path))
#创建数据加载器
from oldcare.datasets import SimpleDatasetLoader
sdl = SimpleDatasetLoader(preprocessors=[aap, iap])
(data, labels) = sdl.load(imagePaths, 500, True)

data = data.astype("float") / 255.0 # 特征缩放，是非常重要的步骤

# 对标签进行one-hot编码
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder().fit(labels)
from tensorflow.keras.utils import to_categorical
labels = to_categorical(le.transform(labels), 2)

from sklearn.model_selection import train_test_split
(trainX, testX, trainY, testY) = train_test_split(data,
   labels, test_size=0.20, stratify=labels, random_state=42)
print("[INFO] compiling model...")
#创建MiniVGGNet实例
from oldcare.conv import MiniVGGNet
model = MiniVGGNet.build(width=TARGET_WIDTH, 
                        height=TARGET_HEIGHT, depth=1, classes=2)
#创建优化器
from tensorflow.keras.optimizers import SGD
opt = SGD(learning_rate=LR_INIT, decay=DECAY, momentum = MOMENTUM, nesterov=True)
#编译模型
model.compile(loss="categorical_crossentropy", optimizer=opt, metrics=["accuracy"])
from oldcare.callbacks import TrainingMonitor
callbacks = [TrainingMonitor(output_plot_path)]

print("[INFO] training network...")
H = model.fit(trainX, trainY, validation_data=(testX, testY), batch_size=BATCH_SIZE, epochs=EPOCHS,
callbacks = callbacks, verbose=1)
print("[INFO] evaluating network...")
predictions = model.predict(testX, batch_size=64)
#输出分类报告
from sklearn.metrics import classification_report
print(classification_report(testY.argmax(axis=1), predictions.argmax(axis=1), target_names=le.classes_))

print("[INFO] serializing network...")
model.save(output_model_path)





