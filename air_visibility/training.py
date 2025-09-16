import os
import keras
from keras import layers
import numpy as np
import cv2 as cv
import csv
import random
import config

IMAGES_PATH = "./dataset/processed/"
MODEL_PATH = "./output/model.keras"

def extract_filename(label_csv_row):
    return label_csv_row[0]

def extract_label(label_csv_row):
    return label_csv_row[1]

class DataGenerator(keras.utils.Sequence):
    def __init__(self, labels, batch_size, shuffle=True, **kwargs):
        super().__init__(**kwargs)
        
        self.labels = labels
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.indexes = []
        self.on_epoch_end()

    def __len__(self):
        return int(np.floor(len(self.labels) / self.batch_size))

    def __getitem__(self, index):
        indexes = self.indexes[index*self.batch_size:(index+1)*self.batch_size]
        labels_chunk = [self.labels[k] for k in indexes]

        in_rgb, in_sift, in_flow, label = self.__data_generation(labels_chunk)
        return ((in_rgb, in_sift, in_flow), label)

    def on_epoch_end(self):
        self.indexes = np.arange(len(self.labels))
        if self.shuffle == True:
            np.random.shuffle(self.indexes)

    def __category_to_label(self, cat):
        if cat == "SMALL":
            return [1, 0, 0]
        elif cat == "MEDIUM":
            return [0, 1, 0]
        return [0, 0, 1]

    def __data_generation(self, labels_chunk):
        rgb_imgs = np.empty((self.batch_size, config.RGB_IMG_HEIGHT, config.RGB_IMG_WIDTH, 3))
        sift_imgs = np.empty((self.batch_size, config.SIFT_FLOW_IMG_HEIGHT, config.SIFT_FLOW_IMG_WIDTH, 3))
        flow_imgs = np.empty((self.batch_size, config.SIFT_FLOW_IMG_HEIGHT, config.SIFT_FLOW_IMG_WIDTH, 3))
        labels = np.empty((self.batch_size, len(config.BETAS)))

        for idx, label in enumerate(labels_chunk):
            labels[idx] = self.__category_to_label(extract_label(label))
            base_path = os.path.join(IMAGES_PATH, str(extract_filename(label)))
            rgb_imgs[idx] = cv.imread(base_path + "_rgb.png") / 255
            sift_imgs[idx] = cv.imread(base_path + "_sift.png") / 255
            flow_imgs[idx] = cv.imread(base_path + "_flow.png") / 255

        return rgb_imgs, sift_imgs, flow_imgs, labels

def get_architecture():
    def conv_layer_2(inputs, filters):
        layer = layers.Conv2D(filters, 1, activation="relu")(inputs)
        layer = layers.Conv2D(filters, 3, activation="relu")(layer)
        layer = layers.MaxPooling2D(2, 2)(layer)
        return layer

    def conv_layer_3(inputs, filters):
        layer = layers.Conv2D(filters, 1, activation="relu")(inputs)
        layer = layers.Conv2D(filters, 3, strides=(2, 2), activation="relu")(layer)
        layer = layers.Conv2D(filters, 1, activation="relu")(layer)
        layer = layers.MaxPooling2D(2, 2)(layer)
        return layer
    
    inputs_rgb = keras.Input(shape=(config.RGB_IMG_HEIGHT, config.RGB_IMG_WIDTH, 3))
    rgb = conv_layer_2(inputs_rgb, 64)

    inputs_sift = keras.Input(shape=(config.SIFT_FLOW_IMG_HEIGHT, config.SIFT_FLOW_IMG_WIDTH, 3))
    sift = conv_layer_2(inputs_sift, 64)

    inputs_flow = keras.Input(shape=(config.SIFT_FLOW_IMG_HEIGHT, config.SIFT_FLOW_IMG_WIDTH, 3))
    flow = conv_layer_2(inputs_flow, 64)

    sift_flow = sift + flow
    sift_flow = layers.Resizing(rgb.shape[1], rgb.shape[2])(sift_flow)
    rgb = rgb + sift_flow

    rgb = conv_layer_2(rgb, 128)
    sift_flow_1 = conv_layer_2(sift_flow, 128)
    sift_flow_2 = conv_layer_2(sift_flow, 128)

    sift_flow = sift_flow_1 + sift_flow_2
    rgb = rgb + sift_flow

    rgb = conv_layer_3(rgb, 256)
    sift_flow_1 = conv_layer_3(sift_flow, 256)
    sift_flow_2 = conv_layer_3(sift_flow, 256)

    sift_flow = sift_flow_1 + sift_flow_2
    sift_flow = layers.AveragePooling2D(2, 2)(sift_flow)
    rgb = layers.AveragePooling2D(2, 2)(rgb)

    rgb_sift_flow = rgb + sift_flow

    fc = layers.Flatten()(rgb_sift_flow)
    fc = layers.Dense(128)(fc)
    output_layer = layers.Dense(len(config.BETAS), activation="softmax")(fc)
    model = keras.Model((inputs_rgb, inputs_sift, inputs_flow), output_layer, name="estimator")
    return model

labels = []
with open('./dataset/labels.csv', mode='r') as file:
    data = csv.reader(file)
    for row in data:
        labels.append([extract_filename(row), extract_label(row)])
random.shuffle(labels)
split = int(len(labels) * 0.2)

dataset_training = DataGenerator(labels[:split], 32)
dataset_validation = DataGenerator(labels[split:], 16)

model = get_architecture()
model.summary()
keras.utils.plot_model(model, "model.png", dpi = 100, show_shapes = True)
model.compile(optimizer=keras.optimizers.Adam(learning_rate = 0.01), loss = 'categorical_crossentropy', metrics = ['accuracy'])
checkpoint = keras.callbacks.ModelCheckpoint(MODEL_PATH, monitor='accuracy', verbose = 1, save_best_only = True, mode = 'max')
history = model.fit(dataset_training, validation_data = dataset_validation, epochs = 100, callbacks = [checkpoint])