# -*- coding: utf-8 -*-

'''
用于实时画出loss曲线和accuracy曲线
'''

# 导入库
from tensorflow.keras.callbacks import BaseLogger
import matplotlib.pyplot as plt
plt.style.use("ggplot")
import numpy as np
import json
import os

# 监控类
class TrainingMonitor(BaseLogger):
    # figPath: 保存的loss和accuracy图片的路径
    # jsonPath: 保存的json文件的路径
    # includeVal: 画出的loss和accuracy曲线是否包含验证集
    # startAt: 从第几个epoch开始训练。
    def __init__(self, figPath, jsonPath=None, includeVal=True, startAt=1):
        super(TrainingMonitor, self).__init__()
        self.figPath = figPath
        self.jsonPath = jsonPath
        self.includeVal = includeVal
        self.startAt = startAt
    
    # 训练开始时，调用该方法
    def on_train_begin(self, logs={}):
        # initialize the history dictionary
        self.H = {}

        # if the JSON history path exists, load the training history
        if self.jsonPath is not None:
            if os.path.exists(self.jsonPath):
                self.H = json.loads(open(self.jsonPath).read())

                # check to see if a starting epoch was supplied
                if self.startAt > 1:
                    # loop over the entries in the history log and trim any entries that are past the starting epoch
                    for k in self.H.keys():
                        self.H[k] = self.H[k][:self.startAt]
    
    # 每当一个epoch结束时，都调用该方法
    def on_epoch_end(self, epoch, logs={}):
        # loop over the logs and update the loss, accuracy, etc. for the entire training process
        for (k, v) in logs.items():
            l = self.H.get(k, [])
            l.append(np.float(v))
            
            self.H[k] = l

        # check to see if the training history should be serialized to file
        if self.jsonPath is not None:
            f = open(self.jsonPath, "w")
            f.write(json.dumps(self.H))
            f.close()

        # 画出曲线
        N = np.arange(1, len(self.H["loss"])+1)
        
        loss_plot_file = os.path.splitext(self.figPath)[0] + '_loss' + os.path.splitext(self.figPath)[1]
        accuracy_plot_file = os.path.splitext(self.figPath)[0] + '_accuracy' + os.path.splitext(self.figPath)[1]
        
        # 画出Loss曲线，并保存图片
        plt.figure()
        plt.plot(N, self.H["loss"], label="train_loss")
        if self.includeVal:
            plt.plot(N, self.H["val_loss"], label="val_loss")
        plt.title("Training Loss [Epoch {}]".format(len(self.H["loss"])))
        plt.xlabel("Epoch #")
        plt.ylabel("Loss")
        plt.legend()
        
        plt.savefig(loss_plot_file)
        plt.close()
        
        # 画出Accuracy曲线，并保存图片  
        plt.figure()
        plt.plot(N, self.H["accuracy"], label="train_accuracy")
        if self.includeVal:
            plt.plot(N, self.H["val_accuracy"], label="val_accuracy")
        plt.title("Training Accuracy [Epoch {}]".format(len(self.H["loss"])))
        plt.xlabel("Epoch #")
        plt.ylabel("Accuracy")
        plt.legend()
        
        plt.savefig(accuracy_plot_file)
        plt.close()






