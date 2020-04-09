# set the matplotlib backend so figures can be saved in the background
import matplotlib
# matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import argparse
import random
import os
from sklearn.preprocessing import LabelBinarizer, LabelEncoder
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.metrics import confusion_matrix
from keras.models import Sequential
from keras.layers.normalization import BatchNormalization
from keras.layers.convolutional import Conv1D
from keras.layers.convolutional import MaxPooling1D
from keras.preprocessing.image import ImageDataGenerator
from keras.layers.core import Activation
from keras.layers.core import Flatten
from keras.layers.core import Dropout
from keras.layers.core import Dense
from keras.optimizers import Adam
from keras.utils import np_utils
from keras import backend as K
from PIL import Image



""" ARGPARSE """
"""
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--dataset", required=True,
	help="path to input dataset (i.e., directory of images)")
ap.add_argument("-m", "--model", required=True,
	help="path to output model")
ap.add_argument("-l", "--labelbin", required=True,
	help="path to output label binarizer")
ap.add_argument("-p", "--plot", type=str, default="plot.png",
	help="path to output accuracy/loss plot")
args = vars(ap.parse_args())
"""

# initialize the number of epochs to train for, initial learning rate,
# batch size, and image dimensions
EPOCHS = 100
INIT_LR = 1e-3
BS = 32
IMAGE_DIMS = (2000/4, 256/4, 1)

# initialize the data and labels
data = []
labels = []
print('LOADING DATA...')

""" LOAD THE IMAGES """
directory = '/Users/greysonbrothers/Desktop/ /- python/- data science/PROJECTS/- Neural Networks/TOILET PROJECT/training_images/'
for folder in os.listdir(directory):
    if folder in ['.DS_Store']:
        continue    
    # loop over the input images
    for imagePath in os.listdir(directory + folder + '/'):
        if imagePath == '.DS_Store':
            continue
        # load the image, pre-process it, and store it in the data list
        image = Image.open(directory + folder + '/' + imagePath)
        image = image.resize((int(IMAGE_DIMS[1]), int(IMAGE_DIMS[0])))
        image = np.asarray(image) 
        data.append(image)
        labels.append(folder) 
    print('.')
print('LOADING COMPLETE')


""" ASSIGN DATA TO TESTING SETS """
data = np.array(data)/255
labels = np.array(labels)

# 60 - 20 - 20 split of the data
X_train, X_test, Y_train, Y_test = train_test_split(data, labels, test_size=0.2, random_state=42)
X_train, X_val, Y_train, Y_val = train_test_split(X_train, Y_train, test_size=0.25, random_state=42)

""" ENCODE LABELS """
encoder = LabelEncoder()
y_train = np_utils.to_categorical(encoder.fit_transform(Y_train))
y_val = np_utils.to_categorical(encoder.fit_transform(Y_val))
y_test = np_utils.to_categorical(encoder.fit_transform(Y_test))
num_classes = len(y_test[0])

""" OPTIONAL AUGMENTATION """
# construct the image generator for data augmentation
#aug = ImageDataGenerator(rotation_range=25, width_shift_range=0.1,
#	height_shift_range=0.1, shear_range=0.2, zoom_range=0.2,
#	horizontal_flip=True, fill_mode="nearest")



""" CONSTRUCT THE MODEL """
print('\nBUILDING MODEL')
model = Sequential()
input_shape = IMAGE_DIMS
pool = 2

#1 CONV => RELU => POOL
model.add(Conv1D(32, 3, padding='same', activation='relu', input_shape=(int(IMAGE_DIMS[0]), 64)))
model.add(BatchNormalization(axis=-1))
model.add(MaxPooling1D(pool_size=pool))
          
#2 (CONV => RELU) * 2 => POOL            
model.add(Conv1D(64, 3, padding='same', activation='relu'))
model.add(BatchNormalization(axis=-1))
model.add(Conv1D(64, 3, padding='same', activation='relu'))
model.add(BatchNormalization(axis=-1))
model.add(MaxPooling1D(pool_size=pool))
downsize = pow(pool, 2)


#3 (CONV => RELU) * 2 => POOL            
model.add(Conv1D(64, 3, padding='same', activation='relu'))
model.add(BatchNormalization(axis=-1))
model.add(Conv1D(64, 3, padding='same', activation='relu'))
model.add(BatchNormalization(axis=-1))
model.add(MaxPooling1D(pool_size=pool))
downsize = pow(pool, 3)
model.add(Dropout(0.1))

#4 (CONV => RELU) * 2 => POOL            
model.add(Conv1D(64, 3, padding='same', activation='relu'))
model.add(BatchNormalization(axis=-1))
model.add(Conv1D(64, 3, padding='same', activation='relu'))
model.add(BatchNormalization(axis=-1))
model.add(MaxPooling1D(pool_size=pool))
downsize = pow(pool, 4)
model.add(Dropout(0.1))

#5 (CONV => RELU) * 2 => POOL            
model.add(Conv1D(64, 3, padding='same', activation='relu'))
model.add(BatchNormalization(axis=-1))
model.add(Conv1D(64, 3, padding='same', activation='relu'))
model.add(BatchNormalization(axis=-1))
model.add(MaxPooling1D(pool_size=pool))
downsize = pow(pool, 5)
model.add(Dropout(0.1))

#6 (CONV => RELU) * 2 => POOL            
model.add(Conv1D(64, 3, padding='same', activation='relu'))
model.add(BatchNormalization(axis=-1))
model.add(Conv1D(64, 3, padding='same', activation='relu'))
model.add(BatchNormalization(axis=-1))
model.add(MaxPooling1D(pool_size=pool))
downsize = pow(pool, 6)
model.add(Dropout(0.15))

#7 (CONV => RELU) * 2 => POOL            
model.add(Conv1D(64, 3, padding='same', activation='relu'))
model.add(BatchNormalization(axis=-1))
model.add(Conv1D(64, 3, padding='same', activation='relu'))
model.add(BatchNormalization(axis=-1))
model.add(MaxPooling1D(pool_size=pool))
model.add(Dropout(0.1))
model.add(Flatten())

# FC Layer
model.add(Dense(64*64))
model.add(Activation('relu'))
model.add(BatchNormalization())
model.add(Dropout(0.5))

# FINAL LAYER SOFTMAX
model.add(Dense(num_classes))
model.add(Activation('softmax'))



""" TRAIN THE MODEL """
print("TRAINING MODEL...")
opt = Adam(lr=INIT_LR, decay=INIT_LR / EPOCHS)
model.compile(loss="categorical_crossentropy", optimizer=opt, metrics=["accuracy"])
history = model.fit(X_train, y_train, batch_size=BS, epochs=EPOCHS, validation_data=(X_val, y_val))



""" PRINT ACCURACY """     
result = model.predict(X_test)
correct = [(np.argmax(y_test[i])== np.argmax(result[i])) for i in range(len(y_test))]
acc = round(100*sum(correct)/len(correct), 2)
print("Accuracy: ", round(acc, 2), "%", sep='')


""" PLOT CONFUSION MATRIX """
y_pred = [np.argmax(i) for i in result]
y_pred = pd.DataFrame(encoder.inverse_transform(y_pred))
conf_mat = confusion_matrix(Y_test, y_pred, labels=encoder.classes_)
conf_mat = [np.around(i/sum(i),2) for i in conf_mat]  # normalize entries

fig, ax = plt.subplots(figsize=(9,8))
ax = sns.heatmap(conf_mat, cmap='Blues', annot=True, xticklabels=encoder.classes_, yticklabels=encoder.classes_)
ax.tick_params(labelsize=6)
plt.title('2 Accuracy: ' + str(acc))
plt.xlabel('Predictions')
plt.ylabel('True Values')
plt.tight_layout()



# Plot training & validation accuracy values
fig1 = plt.figure(figsize=(6,8))
ax1 = fig1.add_subplot(2,1,1)
ax1.plot(history.history['accuracy'])
ax1.plot(history.history['val_accuracy'])
plt.title('2 Model accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['Train', 'Test'], loc='upper left')

# Plot training & validation loss values
ax2 = fig1.add_subplot(2,1,2)
ax2.plot(history.history['loss'])
ax2.plot(history.history['val_loss'])
plt.title('2 Model loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend(['Train', 'Test'], loc='upper left')
plt.tight_layout()




# 50 epochs, 79.13%

# 7 layers 
#   Accuracy: 72.17%

# 7 Layers, 0.1 dropout
#   Accuracy: 75.65%

# 7 Layers, 0.15 dropout 
#   Accuracy: 72.17%
#   Accuracy: 70.43%

# 7 Layers, 0.1 dropout, 100 epochs, 
#   Accuracy: 77.39%
#   Accuracy: 81.74%
#   Accuracy: 80.87%
#   Accuracy: 76.52%
#   Accuracy: 73.91%
#   Accuracy: 74.78%
#   Accuracy: 81.74%












