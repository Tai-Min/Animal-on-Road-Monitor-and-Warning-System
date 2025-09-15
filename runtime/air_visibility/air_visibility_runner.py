from threading import Thread, Event
import time
import tensorflow as tf
import numpy as np
import cv2 as cv
from . import config
from .model import classes

class AirVisibilityRunner:
    def __init__(self, model_path, callback, cam_0, cam_1):
        self.thread_event = Event()
        self.thread = None
        self.model = tf.saved_model.load(model_path)
        self.cb = callback
        self.c0 = cam_0
        self.c1 = cam_1

    def __get_sift_img(self, img):
        img_copy = img.copy()
        img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        img_gray = cv.resize(img, (config.sift_flow_width, config.sift_flow_height))

        sift = cv.SIFT_create()
        kp = sift.detect(img_gray, None)
        img_sift = cv.drawKeypoints(img_gray, kp, img_copy)
        return img_sift

    def __get_flow_img(self, img, next_img):
        img_gray = cv.resize(img, (config.sift_flow_width, config.sift_flow_height))
        hsv = np.zeros_like(img_gray)
        img_gray = cv.cvtColor(img_gray,cv.COLOR_BGR2GRAY)
        
        next_img_gray = cv.resize(next_img, (config.sift_flow_width, config.sift_flow_height))
        next_img_gray = cv.cvtColor(next_img_gray,cv.COLOR_BGR2GRAY)
        
        flow = cv.calcOpticalFlowFarneback(img_gray, next_img_gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        mag, ang = cv.cartToPolar(flow[...,0], flow[...,1])
        
        hsv[...,1] = 255
        hsv[...,0] = ang * 180/ np.pi / 2
        hsv[...,2] = cv.normalize(mag, None, 0, 255, cv.NORM_MINMAX)

        img_flow = cv.cvtColor(hsv, cv.COLOR_HSV2BGR)
        return img_flow

    def __get_result(self, res):
        res = res.numpy()
        val_max = np.argmax(res)
        
        return classes.classes_names[val_max]

    def __inference_loop(self):
        while not self.thread_event.is_set():
            data = None

            f0 = self.c0.get_frame()
            f1 = self.c1.get_frame()
            time.sleep(0.2)

            f0_next = self.c0.get_frame()
            
            desired_shape = config.output_width*config.output_height*3
            if f0 is not None and f1 is not None and f0_next is not None and \
                np.prod(f0.shape) == desired_shape and np.prod(f1.shape) == desired_shape and\
                np.prod(f0_next.shape) == desired_shape:

                f0_sift = self.__get_sift_img(f0)
                f0_flow = self.__get_flow_img(f0, f0_next)

                f0 = cv.resize(f0.copy(), (config.rgb_height, config.rgb_width))

                f0.shape = (1, config.rgb_height, config.rgb_width, 3)
                f0_sift.shape = (1, config.sift_flow_height, config.sift_flow_width, 3)
                f0_flow.shape = (1, config.sift_flow_height, config.sift_flow_width, 3)

                result = self.model.serve([f0, f0_sift, f0_flow])
                result = self.__get_result(result)

                if self.cb != None:
                    self.cb(result)

            if data is not None and np.prod(data.shape) == 240*320: #TODO: img size
                data.shape = (1, 240, 320, 1)
                
    def start(self):
        if self.thread:
            
            ("Thread already running")

        self.c0.start(0, config.camera_width, config.camera_height, config.camera_flip, config.camera_framerate)
        self.c1.start(1, config.camera_width, config.camera_height, config.camera_flip, config.camera_framerate)
        
        self.thread_event.clear()
        self.thread = Thread(target=self.__inference_loop)
        self.thread.start()

    def stop(self):
        if self.thread:
            self.c0.stop()
            self.c1.stop()
            self.thread_event.set()
            self.thread.join()
            self.thread = None
        else:
            print("Thread not running, nothing to stop")

class CameraMock():
    def __init__(self, frame_path, frame_next_path):
        self.frame = cv.imread(frame_path)
        self.frame = cv.resize(self.frame, (config.output_width, config.output_height))

        self.frame_next = cv.imread(frame_next_path)
        self.frame_next = cv.resize(self.frame_next, (config.output_width, config.output_height))

        self.tick_tock = False

    def start(self, sensor_id, width, height, flip, framerate):
        pass

    def stop(self):
        pass

    def get_frame(self):
        self.tick_tock = not self.tick_tock
        if self.tick_tock:
            return self.frame
        else:
            return self.frame_next

if __name__ == "__main__":
    import signal
    import sys
    import os

    runner = None

    def sigint_handler(signal, frame):
        if runner:
            runner.stop()
        sys.exit(0)

    def callback(res):
        print(res)

    frame_path = os.path.join(os.path.dirname(__file__), "../media/f0.png")
    frame_next_path = os.path.join(os.path.dirname(__file__), "../media/f0_next.png")
    c0 = CameraMock(frame_path, frame_next_path)
    c1 = CameraMock(frame_path, frame_next_path)
    runner = AirVisibilityRunner(os.path.join(os.path.dirname(__file__), "model/"), callback, c0, c1)
    signal.signal(signal.SIGINT, sigint_handler)

    runner.start()

    while True:
        time.sleep(1)
        #classifier.add_animal_detection_to_queue(img.copy())
