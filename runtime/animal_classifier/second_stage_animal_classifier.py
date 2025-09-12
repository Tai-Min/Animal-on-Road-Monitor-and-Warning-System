from threading import Lock

class SecondStageClassifier:
    def __init__(self):
        self.animal_classifier_queue = []
        self.animal_classifier_mutex = Lock()

    def add_animal_detection_to_queue(self, img):
        with self.animal_classifier_mutex:
            self.animal_classifier_queue.append(img)