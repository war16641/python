import numpy as np
import tensorflow as tf
import matplotlib
from matplotlib import pyplot as plt

matplotlib.rcParams['font.size'] = 20
matplotlib.rcParams['figure.titlesize'] = 20
matplotlib.rcParams['figure.figsize'] = [9, 7]
matplotlib.rcParams['font.family'] = ['STKaiTi']
matplotlib.rcParams['axes.unicode_minus']=False


def load_mnist():
    #define the directory where mnist.npz is(Please watch the '\'!)
    path = r"C:\Users\niyinhao\Downloads\mnist.npz"
    f = np.load(path)
    x_train, y_train = f['x_train'],f['y_train']
    x_test, y_test = f['x_test'],f['y_test']
    f.close()
    return (x_train, y_train), (x_test, y_test)


#载入数据
(train_image,train_label),(test_image,test_lable) = load_mnist()


#网络架构
from keras import models
from keras import layers
network=models.Sequential()
network.add(layers.Dense(512,activation='relu',input_shape=(28*28,)))
network.add(layers.Dense(10,activation='softmax'))


#编译
network.compile(optimizer='rmsprop',
                loss='categorical_crossentropy',
                metrics=['accuracy'])

#准备图像数据
train_image=train_image.reshape((60000,28*28))
train_image=train_image.astype('float32')/255
test_image=test_image.reshape((10000,28*28))
test_image=test_image.astype('float32')/255


#准备标签
from keras.utils import to_categorical
train_label=to_categorical(train_label)
test_lable=to_categorical(test_lable)

#训练
network.fit(train_image,train_label,epochs=5,batch_size=128)

#测试
test_loss,test_acc=network.evaluate(test_image,test_lable)
print('test_acc',test_acc)
a=1