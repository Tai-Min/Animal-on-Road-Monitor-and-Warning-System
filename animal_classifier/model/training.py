import keras
from keras import layers
import config 
import os

DATASET_PATH = "./dataset/processed/"
TRAINING_BATCH_SIZE = 32

train_set = keras.utils.image_dataset_from_directory(
DATASET_PATH,
validation_split=0.2,
subset="training",
seed=1,
image_size=(config.CAMERA_HEIGHT, config.CAMERA_WIDTH),
batch_size=TRAINING_BATCH_SIZE)

validation_set = keras.utils.image_dataset_from_directory(
DATASET_PATH,
validation_split=0.2,
subset="validation",
seed=1,
image_size=(config.CAMERA_HEIGHT, config.CAMERA_WIDTH),
batch_size=TRAINING_BATCH_SIZE)

num_classes = len([file for file in os.listdir(DATASET_PATH)])

model = keras.Sequential()

resnet = keras.applications.VGG16(
    include_top=False,
    input_shape=(config.CAMERA_HEIGHT, config.CAMERA_WIDTH, 3),
    pooling='avg',
    classes=num_classes,
    weights='imagenet')

for layer in resnet.layers:
    layer.trainable=False

model.add(resnet)
model.add(layers.Flatten())
model.add(layers.Dense(128, activation='relu'))
model.add(layers.Dense(num_classes, activation='softmax'))

model.summary()

model.compile(optimizer=keras.optimizers.Adam(learning_rate=0.001), loss='sparse_categorical_crossentropy', metrics=['accuracy'])

history = model.fit(
    train_set,
    validation_data=validation_set,
    epochs=10)