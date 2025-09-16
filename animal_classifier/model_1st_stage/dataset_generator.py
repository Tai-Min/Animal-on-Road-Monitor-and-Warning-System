import os
import glob
import cv2 as cv
import config

def process_image(img_path, export_path, class_name, idx):
    
    img = cv.imread(img_path)
    img = cv.resize(img, (config.CAMERA_WIDTH, config.CAMERA_HEIGHT), interpolation= cv.INTER_CUBIC)
    gimg = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    zeros = "0" * (3 - len(str(idx)))
    cv.imwrite(os.path.join(export_path, class_name + "." + zeros + str(idx) + ".jpg"), gimg)
    return idx + 1

if __name__ == "__main__":
    CLASSES_PATH = "./dataset/animals/"
    EXPORT_PATH = "./dataset/processed/"

    if not os.path.exists(EXPORT_PATH):
        os.makedirs(EXPORT_PATH)

    classes_folders = [file for file in os.listdir(CLASSES_PATH)]

    idx = 0

    assert(len(classes_folders) == len(config.ANIMAL_TYPES), "Number of folders inside processed dataset must be equal to len(ANIMAL_FIRST_STAGE_TYPES) from project_config.py")

    for animal_class in classes_folders:
        assert(animal_class not in config.ANIMAL_TYPES, f"{animal_class} is not present in ANIMAL_FIRST_STAGE_TYPES")

        images = glob.glob(os.path.join(CLASSES_PATH, animal_class, "*.jpg"))

        animal_export_path = os.path.join(EXPORT_PATH, animal_class)

        if not os.path.exists(animal_export_path):
            os.makedirs(animal_export_path)

        for img in images:
            idx = process_image(img, animal_export_path, animal_class, idx)