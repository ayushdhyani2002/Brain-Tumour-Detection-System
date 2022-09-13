# -*- coding: utf-8 -*-
"""Brain Tumor Detection System.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1531Yl5_6psDPMvOelX8w5-8ZA7PMhj-4
"""

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
import numpy as np
import os

import tensorflow as tf
import cv2
from tensorflow import keras
from tensorflow.keras import layers, Input
from keras.layers import InputLayer, MaxPooling2D, Flatten, Dense, Conv2D, Dropout
from keras.losses import BinaryCrossentropy
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import preprocess_input, decode_predictions, ResNet50
from tensorflow.keras.optimizers import Adam, SGD

from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split
from PIL.Image import open

from  matplotlib import pyplot as plt
import matplotlib.image as mpimg
import random
# %matplotlib inline

from google.colab import drive
drive.mount('/content/drive')

IMAGE_DATASET = "/content/drive/MyDrive/Brain Tumor"
IMAGE_DATASET_RAW = r"/content/drive/MyDrive/bt_dataset_t3.csv"
WORKING_FOLDER = "/content/drive/MyDrive/Brain Tumor"
IMG_HEIGHT = 224
IMG_WIDTH = 224
EPOCHS = 50

cortex_df = pd.read_csv("/content/drive/MyDrive/Brain Tumor (1).csv")
cortex_df.head()

plt.figure(figsize=(20,20))
test_folder="/content/drive/MyDrive/Brain Tumor" 
for i in range(5):
    file = random.choice(os.listdir(test_folder)) 
    image_path= os.path.join(test_folder, file)
    img=mpimg.imread(image_path)
    ax=plt.subplot(1,5,i+1)
    ax.title.set_text(file)
    plt.imshow(img)

dataset_df = pd.DataFrame()
dataset_df["Image"] = cortex_df["Image"]
dataset_df["Class"] = cortex_df["Class"] # preprocessing tech
path_list = []
for img_path in os.listdir(IMAGE_DATASET):
    path_list.append( os.path.join(IMAGE_DATASET,img_path))
path_dict = {os.path.splitext(os.path.basename(x))[0]: x for x in path_list}
dataset_df["paths"] = cortex_df["Image"].map(path_dict.get)
dataset_df["pixels"] = dataset_df["paths"].map(lambda x:np.asarray(open(x).resize((IMG_HEIGHT,IMG_WIDTH))))
dataset_df.head()

image_list = []
for i in range(len(dataset_df)):
    brain_image = dataset_df["pixels"][i].astype(np.float32)
    brain_image /= 255
    image_list.append(brain_image)
X = np.array(image_list)
print(X.shape)

y = np.array(dataset_df.Class)
y.shape

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
print('The shape of the X_train :'+' '+str(X_train.shape))
print('The size of the X_train :'+' '+str(X_train.shape[0]))
print('The shape of the X_test :'+' '+str(X_test.shape))
print('The size of the X_test:'+' '+str(X_test.shape[0]))

def model(input_shape):

    model = Sequential()
    
    model.add(Input(shape=input_shape))
    
    model.add(Conv2D(16, kernel_size=3, strides=(2, 2), padding="same", activation="relu", kernel_initializer="he_normal"))
    model.add(Conv2D(16, kernel_size=3, strides=(2, 2), padding="same", activation="relu", kernel_initializer="he_normal"))
    model.add(MaxPooling2D(pool_size=(2, 2), data_format="channels_last", padding='same'))
            
    model.add(Conv2D(32, kernel_size=3, strides=(2, 2), padding="same", activation="relu", kernel_initializer="he_normal"))
    model.add(Conv2D(32, kernel_size=3, strides=(2, 2), padding="same", activation="relu", kernel_initializer="he_normal")) #relu piecewise linear function that will output the input directly if it is positive, otherwise, it will output zero
    model.add(MaxPooling2D(pool_size=(2, 2), data_format="channels_last", padding='same'))
  
    model.add(Conv2D(64, kernel_size=3, strides=(2, 2), padding="same", activation="relu", kernel_initializer="he_normal")) #activation function is the last comp of cnn to increase non linearity of the output
    model.add(Conv2D(64, kernel_size=3, strides=(2, 2), padding="same", activation="relu", kernel_initializer="he_normal"))
    model.add(MaxPooling2D(pool_size=(2, 2), data_format="channels_last", padding='same'))
    

    
    model.add(Flatten())
    model.add(Dense(256, activation="relu")) #kernel refers to a method that allows us to apply linear classifiers to non-linear problems
    model.add(Dense(128, activation="relu")) #padding amounts to the pixels added to an image when it is being processed by the kernel of cnn

    model.add(Dense(1, activation="sigmoid"))    
    return model

model = model(input_shape = (IMG_HEIGHT, IMG_WIDTH, 3))

model.summary()

optimizer = SGD(learning_rate=0.01)
loss_fn = BinaryCrossentropy(from_logits=True)
model.compile(optimizer=optimizer, loss=loss_fn, metrics=['accuracy'])

history = model.fit(x=X_train, y=y_train, epochs=EPOCHS, batch_size=10)

model.save("BrainTumorv7")

loss = history.history["loss"]
acc = history.history["accuracy"]

epoch = np.arange(EPOCHS)
plt.plot(epoch, loss)
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.title('Training Loss')
plt.legend(['train', 'val'])

epoch = np.arange(EPOCHS)
plt.plot(epoch, acc)
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.title('Training Accuracy');

eval_score = model.evaluate(X_test, y_test)
print("Test loss:", eval_score[0])
print("Test accuracy:", eval_score[1])