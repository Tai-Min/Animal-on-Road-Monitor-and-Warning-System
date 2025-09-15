from threading import Lock, Thread, Event
import tensorflow as tf
import numpy as np
from model import classes

class SecondStageClassifier:
    def __init__(self, model_path, callback):
        self.animal_classifier_queue = []
        self.animal_classifier_mutex = Lock()
        self.thread_event = Event()
        self.thread = None
        self.model = tf.saved_model.load(model_path)
        self.cb = callback

    def __get_readable_result(self, inference):
        inference = inference.numpy()
        inference.shape = (len(classes.classes_names))
        res = []
        for class_name, i in zip(classes.classes_names, range(np.prod(inference.shape))):
            res.append({class_name : float(inference[i])})
        return res

    def __get_best_result(self, result):
        best_val = 0
        best_key = None
        for res in result:
            key = list(res.keys())[0]
            val = res[key]

            if val > best_val:
                best_val = val
                best_key = key

        return [best_key, best_val]

    def __inference_loop(self):
        while not self.thread_event.is_set():
            data = None

            with self.animal_classifier_mutex:
                if len(self.animal_classifier_queue):
                    data = self.animal_classifier_queue.pop(0)

            if data is not None and np.prod(data.shape) == 240*320:
                data.shape = (1, 240, 320, 1)
                result = self.model.serve(data)
                result = self.__get_readable_result(result)
                result = self.__get_best_result(result)

                if self.cb != None:
                    self.cb(result)


    def add_animal_detection_to_queue(self, img):
        with self.animal_classifier_mutex:
            self.animal_classifier_queue.append(img)

    def start(self):
        if self.thread:
            print("Thread already running")

        self.thread_event.clear()
        self.thread = Thread(target=self.__inference_loop)
        self.thread.start()

    def stop(self):
        if self.thread:
            self.thread_event.set()
            self.thread.join()
            self.thread = None
        else:
            print("Thread not running, nothing to stop")

if __name__ == "__main__":
    import signal
    import sys
    import time
    import cv2 as cv
    import os

    classifier = None

    def sigint_handler(signal, frame):
        if classifier:
            classifier.stop()
        sys.exit(0)

    def callback(res):
        print(res)

    classifier = SecondStageClassifier(os.path.join(os.path.dirname(__file__), "model/"), callback)
    signal.signal(signal.SIGINT, sigint_handler)

    classifier.start()

    img = cv.imread(os.path.join(os.path.dirname(__file__), "../media/cow.jpg"))
    img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    while True:
        time.sleep(1)
        classifier.add_animal_detection_to_queue(img.copy())
