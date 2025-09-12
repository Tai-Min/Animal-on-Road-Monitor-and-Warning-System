import keras
from keras import layers
import config 
import os

DATASET_PATH = "./dataset/processed/"
MODEL_PATH = "./output/model.keras"
TRAINING_BATCH_SIZE = 32

train_set = keras.utils.image_dataset_from_directory(
DATASET_PATH,
validation_split = 0.2,
subset = "training",
seed = 1,
image_size = (config.CAMERA_HEIGHT, config.CAMERA_WIDTH),
batch_size = TRAINING_BATCH_SIZE)

validation_set = keras.utils.image_dataset_from_directory(
DATASET_PATH,
validation_split = 0.2,
subset = "validation",
seed = 1,
image_size = (config.CAMERA_HEIGHT, config.CAMERA_WIDTH),
batch_size = TRAINING_BATCH_SIZE)

def get_architecture():
    def conv_layer(x, kernel_size, filters, stride = 2):
        f1, f2, f3 = filters

        bn_axis = 3

        x_skip = x

        x = layers.Conv2D(f1, (1, 1), strides = (stride, stride), padding = 'valid')(x)
        x = layers.BatchNormalization(axis = bn_axis)(x)
        x = layers.Activation('relu')(x)
        
        x = layers.Conv2D(f2,  kernel_size = (kernel_size, kernel_size), strides = (1,1), padding = 'same')(x)
        x = layers.BatchNormalization(axis = bn_axis)(x)
        x = layers.Activation('relu')(x)

        x = layers.Conv2D(f3, kernel_size = (1, 1), strides = (1,1), padding = 'valid')(x)
        x = layers.BatchNormalization(axis = bn_axis)(x)

        x_skip = layers.Conv2D(f3, (1, 1), strides = (stride, stride), padding = 'valid')(x_skip)
        x_skip = layers.BatchNormalization(axis = 3)(x_skip)

        x = layers.Add()([x, x_skip])
        x = layers.Activation('relu')(x)

        return x

    def id_layer(x, kernel_size, filters):
        f1, f2, f3 = filters

        bn_axis = 3

        x_skip = x

        x = layers.Conv2D(filters = f1, kernel_size = (1, 1), strides = (1, 1), padding='valid')(x)
        x = layers.BatchNormalization(axis=bn_axis)(x)
        x = layers.Activation('relu')(x)
        
        x = layers.Conv2D(filters = f2, kernel_size = (kernel_size, kernel_size), strides = (1, 1), padding='same')(x)
        x = layers.BatchNormalization(axis=bn_axis)(x)
        x = layers.Activation('relu')(x)

        x = layers.Conv2D(filters = f3, kernel_size = (1, 1), strides = (1, 1), padding='valid')(x)
        x = layers.BatchNormalization(axis=bn_axis)(x)
        
        x = layers.Add()([x, x_skip])
        x = layers.Activation('relu')(x)

        return x

    input = layers.Input((config.CAMERA_HEIGHT, config.CAMERA_WIDTH, 3))

    x = keras.layers.RandomFlip("vertical")(input)
    x = keras.layers.RandomRotation(0.2)(x)
    x = keras.layers.RandomBrightness(0.1)(x)
    x = keras.layers.RandomZoom(0.2)(x)

    x = layers.Conv2D(4, (3, 3), strides=(2, 2))(x)
    x = layers.BatchNormalization(axis = 3)(x)
    x = layers.Activation('relu')(x)
    x = layers.MaxPooling2D((3, 3), strides=(2, 2))(x)

    x = conv_layer(x, 3, [32, 32, 64], 1)
    x = id_layer(x, 3, [32, 32, 64])

    x = conv_layer(x, 3, [64, 64, 128], 1)
    x = id_layer(x, 3, [64, 64, 128])
    x = layers.AveragePooling2D((2, 2))(x)

    x = layers.Flatten()(x)
    output_layer = layers.Dense(len([file for file in os.listdir(DATASET_PATH)]), activation='softmax')(x)
    model = keras.Model(input, output_layer, name="classifier")
    return model

model = get_architecture()

model.summary()
keras.utils.plot_model(model, "model.png", dpi=100, show_shapes=True)
model.compile(optimizer=keras.optimizers.Adam(learning_rate=0.001), loss='sparse_categorical_crossentropy', metrics=['accuracy'])

checkpoint = keras.callbacks.ModelCheckpoint(MODEL_PATH, monitor='val_accuracy', verbose = 1, save_best_only = True, mode = 'max')
history = model.fit(train_set, validation_data = validation_set, epochs=100, callbacks=[checkpoint])