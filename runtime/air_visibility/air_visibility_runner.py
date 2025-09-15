from threading import Thread, Event
import tensorflow as tf
import numpy as np
import camera

class AirVisibilityRunner:
    def __init__(self, model_path, callback, cam_id_0, cam_id_1):
        self.thread_event = Event()
        self.thread = None
        self.model = tf.saved_model.load(model_path)
        self.cb = callback
        self.c0 = camera.Camera()
        self.c1 = camera.Camera()

    def __inference_loop(self):
        while not self.thread_event.is_set():
            data = None

            # TODO get frames

            if data is not None and np.prod(data.shape) == 240*320: #TODO: img size
                data.shape = (1, 240, 320, 1)
                result = self.model.serve(data)

                if self.cb != None:
                    self.cb(result)

    def start(self):
        if self.thread:
            
            ("Thread already running")

        self.c0.start()
        self.c1.start()
        
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

    runner = None

    def sigint_handler(signal, frame):
        if runner:
            runner.stop()
        sys.exit(0)

    def callback(res):
        print(res)

    runner = AirVisibilityRunner(os.path.join(os.path.dirname(__file__), "model/"), callback)
    signal.signal(signal.SIGINT, sigint_handler)

    runner.start()

    img = cv.imread(os.path.join(os.path.dirname(__file__), "../media/cow.jpg"))
    img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    while True:
        time.sleep(1)
        #classifier.add_animal_detection_to_queue(img.copy())
