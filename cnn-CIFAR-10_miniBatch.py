import tensorflow as tf
import pandas as pd
import numpy as np
import re
import matplotlib
from matplotlib import patches
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import keras
from keras.datasets import mnist
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv2D, MaxPooling2D
import pickle
import pickle as cPickle
from keras.datasets import cifar10
from keras.optimizers import SGD
from keras.constraints import maxnorm
from keras.utils import np_utils

from tensorboard import default
from tensorboard import program
import logging
import sys
import time

# name = "miniP-{}".format(int(time.time()))
# tensorboard = program.TensorBoard(log_dir='./logs'.format(name))

#### A class for running TensorBoard in VirtualEnv ####
class TensorBoardTool:
    def __init__(self, dir_path):
        self.dir_path = dir_path
    def run(self):
        # Remove http messages
        log = logging.getLogger('werkzeug').setLevel(logging.ERROR)
        # Start tensorboard server
        tb = program.TensorBoard(default.get_plugins())
        tb.configure(argv=[None, '--logdir', self.dir_path])
        url = tb.launch()
        sys.stdout.write('TensorBoard at %s \n' % url)

# Tensorboard tool launch
tb_tool = TensorBoardTool('./Graph')
tb_tool.run()


IMAGE_SIZE = 24
NUM_EXAMPLES_PER_EPOCH_FOR_TRAIN = 500
NUM_EXAMPLES_PER_EPOCH_FOR_EVAL = 100

MOVING_AVERAGE_DECAY = 0.9999
NUM_EPOCHS_PER_DECAY = 350.0
LEARNING_RATE_DECAY_FACTOR = 0.1
INITIAL_LEARNING_RATE = 0.1

# class AccuracyHistory(keras.callbacks.Callback):
#     def on_train_begin(self, logs={}):
#         self.acc = []
#
#     def on_epoch_end(self, batch, logs={}):
#         self.acc.append(logs.get('acc'))

#### Parameters ####
batch_size = 32
epochs = 1
num_classes = 10


#### Loading Dataset from File ####
def unpickle(file):
    import pickle
    with open(file, 'rb') as fo:
        #dict = pickle.load(fo)
        dict = cPickle.load(fo)
    return dict


pd_tr = pd.DataFrame()
tr_y = pd.DataFrame()

for i in range(1, 6):
    data = unpickle('cifar/data_batch_' + str(i))
    pd_tr = pd_tr.append(pd.DataFrame(data[b'data']))
    tr_y = tr_y.append(pd.DataFrame(data[b'labels']))
    pd_tr['labels'] = tr_y

tr_x = np.asarray(pd_tr.iloc[:, :3072])
tr_y = np.asarray(pd_tr['labels'])
ts_x = np.asarray(unpickle('cifar/test_batch')[b'data'])
ts_y = np.asarray(unpickle('cifar/test_batch')[b'labels'])
labels = unpickle('cifar/batches.meta')[b'label_names']

#### Plotting the data loaded from File ####
def plot_CIFAR(ind):
    arr = tr_x[ind]
    R = arr[0:1024].reshape(32, 32) / 255.0
    G = arr[1024:2048].reshape(32, 32) / 255.0
    B = arr[2048:].reshape(32, 32) / 255.0

    img = np.dstack((R, G, B))
    title = re.sub('[!@#$b]', '', str(labels[tr_y[ind]]))
    fig = plt.figure(figsize=(3, 3))
    ax = fig.add_subplot(111)
    ax.imshow(img, interpolation='bicubic')
    ax.set_title('Category = ' + title, fontsize=15)
    plt.show()

# plot_CIFAR(90)





#### Loading the data using Library which is used for training ####
(x_train, y_train), (x_test, y_test) = cifar10.load_data()

# Convert and pre-processing

y_train = np_utils.to_categorical(y_train, num_classes)
y_test = np_utils.to_categorical(y_test, num_classes)
x_train = x_train.astype('float32')
x_test = x_test.astype('float32')
x_train /= 255
x_test /= 255


print ("y_test size:", y_test.__len__())
print ("x_train", x_train.shape)
print ("y_text", y_test.shape)
print ("x_test", x_test.shape)
print ("y_train", y_train.shape)

x_test_new = np.resize(x_test,(5000, 32, 32, 3))
x_train_new = np.resize(x_train,(5000, 32, 32, 3))
y_train_new = np.resize(x_train,(5000, 10))
y_test_new = np.resize(x_train,(5000, 10))
# x_train_new = np.empty((1000, 32, 32, 3), dtype="float32")  # empty?ones????????????????????
# x_test_new = np.empty((1000, 32, 32, 3), dtype="float32")  # empty?ones????????????????????
# label = np.empty((42000,),dtype="uint8")
#
# y_train_new = np_utils.to_categorical(y_train, num_classes)
# y_test_new = np_utils.to_categorical(y_test, num_classes)
#
# for i in range(1000):
#     x_train_new[i] = x_train[i]
#     y_train_new[i] = y_train[i]
# for j in range(1000):
#     x_test_new[j] = x_test[j]
#     y_test_new[j] = y_test[j]




#### callbacks for keras to be showed in tensorboard ####
tbCallBack = keras.callbacks.TensorBoard(log_dir='./Graph', histogram_freq=0,write_graph=True, write_images=True)



#### Model No.1 (the one designed on saturday) ####
model = Sequential()
model.add(Conv2D(32, kernel_size=(2, 2), activation='relu', input_shape=(32,32,3)))
# model.add(Conv2D(32, kernel_size=(2, 2), activation='relu', input_shape=(32,32,3)))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Conv2D(32, (2, 2), activation='relu'))
model.add(Conv2D(32, (2, 2), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Conv2D(16, (2, 2), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(Flatten())
model.add(Dense(128, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(num_classes, activation='softmax'))

model.compile(loss='categorical_crossentropy',
              optimizer=keras.optimizers.SGD(lr=0.01),
              metrics=['accuracy'])

model.fit(x_train_new, y_train_new,epochs=1, batch_size=32, validation_data=(x_test_new, y_test_new), callbacks=[tbCallBack])



# history = AccuracyHistory()
# plt.plot(range(1, 6), history.acc)
# plt.xlabel('Epochs')
# plt.ylabel('Accuracy')
# plt.show()

#### model copied from internet (https://blog.plon.io/tutorials/cifar-10-classification-using-keras-tutorial/) ####
#
# def base_model():
#     model = Sequential()
#
#     model.add(Conv2D(32, (3, 3), padding='same', activation='relu', input_shape=x_train.shape[1:]))
#     model.add(Dropout(0.2))
#
#     model.add(Conv2D(32, (3, 3), padding='same', activation='relu'))
#     model.add(MaxPooling2D(pool_size=(2, 2)))
#
#     model.add(Conv2D(64, (3, 3), padding='same', activation='relu'))
#     model.add(Dropout(0.2))
#
#     model.add(Conv2D(64, (3, 3), padding='same', activation='relu'))
#     model.add(MaxPooling2D(pool_size=(2, 2)))
#
#     model.add(Conv2D(128, (3, 3), padding='same', activation='relu'))
#     model.add(Dropout(0.2))
#
#     model.add(Conv2D(128, (3, 3), padding='same', activation='relu'))
#     model.add(MaxPooling2D(pool_size=(2, 2)))
#
#     model.add(Flatten())
#     model.add(Dropout(0.2))
#     model.add(Dense(1024, activation='relu', kernel_constraint=maxnorm(3)))
#     model.add(Dropout(0.2))
#     model.add(Dense(num_classes, activation='softmax'))
#
#     sgd = SGD(lr = 0.1, decay=1e-6, momentum=0.9,nesterov=True)
#
# # Train model
#
#     model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])
#     return model
# cnn_n = base_model()
# cnn_n.summary()
#
# # Fit model
#
# cnn = cnn_n.fit(x_train, y_train, batch_size=batch_size, epochs=epochs, validation_data=(x_test,y_test),shuffle=True)
