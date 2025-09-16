import keras
import os
import config

if __name__ == "__main__":
    model = keras.saving.load_model('./output/model.keras')
    model.export("../../runtime/animal_classifier/model/", format="tf_saved_model")