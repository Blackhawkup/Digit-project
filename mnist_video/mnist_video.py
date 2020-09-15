"""

    mnist_video.py

    

"""

import tensorflow as tf
import numpy as np
import os
import matplotlib.pyplot as plt
from PIL import Image

import cv2
from matplotlib import pyplot as plt

def get_mnist_data():
    # get mnist data 
    path = 'mnist.npz'

    # get data - this will be cached 
    mnist = tf.keras.datasets.mnist

    (x_train, y_train),(x_test, y_test) = mnist.load_data(path=path)
    return (x_train, y_train, x_test, y_test)

def train_model(x_train, y_train, x_test, y_test):
    # set up TF model and train 
    # callback 
    class myCallback(tf.keras.callbacks.Callback):
        def on_epoch_end(self, epoch, logs={}):
            print(logs)
            if(logs.get('accuracy') > 0.99):
                print("\nReached 99% accuracy so cancelling training!")
                self.model.stop_training = True
                                
    callbacks = myCallback()

    # normalise 
    x_train, x_test = x_train/255.0, x_test/255.0

    # create model 
    model = tf.keras.models.Sequential([
        tf.keras.layers.Flatten(input_shape=(28, 28)),
        tf.keras.layers.Dense(512, activation=tf.nn.relu),
        tf.keras.layers.Dense(10, activation=tf.nn.softmax)
    ])

    model.compile(optimizer='adam',
                loss='sparse_categorical_crossentropy',
                metrics=['accuracy'])
    print(model.summary())

    # fit model
    history = model.fit(x_train, y_train, epochs=10, callbacks=[callbacks])
    # stats 
    print(history.epoch, history.history['accuracy'][-1])
    return model

def predict(model):
    res = model.predict(x_test[11:12])
    print(res)


# 
# opencv part 
# 

def on_threshold(x):
    pass

def start_cv(model):
    cap = cv2.VideoCapture(0)
    frame = cv2.namedWindow('background')
    cv2.createTrackbar('threshold', 'background', 0, 255, on_threshold)
    background = np.zeros((480, 640), np.uint8)

    while True:
        ret, frame = cap.read()
        frame = cv2.resize(frame, None, fx=0.5, fy=0.5)

        frame[0:480, 0:80] = 0
        frame[0:480, 560:640] = 0
        grayFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        threshold = cv2.getTrackbarPos('threshold', 'background')
        _, thr = cv2.threshold(grayFrame, threshold, 255, cv2.THRESH_BINARY)
        cv2.putText(background, 'X', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
        resizedFrame = thr[240-75:240+75, 320-75:320+75]
        background[240-75:240+75, 320-75:320+75] = resizedFrame

        iconImg = cv2.resize(resizedFrame, (28, 28))
        
        
        cv2.imshow('background', background)
        # cv2.imshow('resized', resizedFrame)
        if cv2.waitKey(1) & 0xff == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def main():

    # load and train data 
    print("getting mnist data...")
    (x_train, y_train, x_test, y_test) = get_mnist_data()
    print("training model...")
    model = train_model(x_train, y_train, x_test, y_test)
    print("starting cv...")
    # show opencv window
    start_cv(model)

# call main
if __name__ == '__main__':
    main()