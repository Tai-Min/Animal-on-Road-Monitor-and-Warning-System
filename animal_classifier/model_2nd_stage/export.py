import keras
import os

if __name__ == "__main__":
    model = keras.saving.load_model('./output/model.keras')
    model.export("../../runtime/animal_classifier/model/", format="tf_saved_model")
    with open("../../runtime/animal_classifier/model/classes.py", 'w') as classes:
        classes.write("classes_names = ")
        classes.write(str(sorted(os.listdir("./dataset/processed"))))