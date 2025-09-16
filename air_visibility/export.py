import keras
import os
import config

if __name__ == "__main__":
    THIS_DIR = os.path.dirname(__file__)
    MODEL_PATH = os.path.join(THIS_DIR, "output/model.keras")
    EXPORT_PATH = os.path.join(THIS_DIR, "../runtime/air_visibility/model/")
    CLASSES_PATH = os.path.join(EXPORT_PATH, "classes.py")

    model = keras.saving.load_model(MODEL_PATH)
    model.export(EXPORT_PATH, format="tf_saved_model")