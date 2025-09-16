import keras
import os

if __name__ == "__main__":
    THIS_DIR = os.path.dirname(__file__)
    MODEL_PATH = os.path.join(THIS_DIR, "output/model.keras")
    EXPORT_PATH = os.path.join(THIS_DIR, "../runtime/air_visibility/model/")

    model = keras.saving.load_model(MODEL_PATH)
    model.export(EXPORT_PATH, format="tf_saved_model")