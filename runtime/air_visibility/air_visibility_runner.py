from threading import Thread, Event
import time
import tensorflow as tf
import numpy as np
import cv2 as cv
from . import config

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
        img_gray = cv.resize(img, (config.SIFT_FLOW_WIDTH, config.SIFT_FLOW_HEIGHT))

        sift = cv.SIFT_create()
        kp = sift.detect(img_gray, None)
        img_sift = cv.drawKeypoints(img_gray, kp, img_copy)
        return img_sift

    def __get_flow_img(self, img, next_img):
        img_gray = cv.resize(img, (config.SIFT_FLOW_WIDTH, config.SIFT_FLOW_HEIGHT))
        hsv = np.zeros_like(img_gray)
        img_gray = cv.cvtColor(img_gray,cv.COLOR_BGR2GRAY)
        
        next_img_gray = cv.resize(next_img, (config.SIFT_FLOW_WIDTH, config.SIFT_FLOW_HEIGHT))
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
        
        return config.BETAS_STR[val_max]

    def __inference_loop(self):
        while not self.thread_event.is_set():
            f0 = self.c0.get_frame()
            f1 = self.c1.get_frame()
            time.sleep(0.2)

            f0_next = self.c0.get_frame()
            
            desired_shape = config.CAMERA_WIDTH*config.CAMERA_HEIGHT*3
            if f0 is not None and f1 is not None and f0_next is not None and \
                np.prod(f0.shape) == desired_shape and np.prod(f1.shape) == desired_shape and\
                np.prod(f0_next.shape) == desired_shape:

                print("Received air visibility frames, estimating visibility...")

                f0_sift = self.__get_sift_img(f0)
                f0_flow = self.__get_flow_img(f0, f0_next)

                f0 = cv.resize(f0.copy(), (config.RGB_HEIGHT, config.RGB_WIDTH))

                f0.shape = (1, config.RGB_HEIGHT, config.RGB_WIDTH, 3)
                f0_sift.shape = (1, config.SIFT_FLOW_HEIGHT, config.SIFT_FLOW_WIDTH, 3)
                f0_flow.shape = (1, config.SIFT_FLOW_HEIGHT, config.SIFT_FLOW_WIDTH, 3)

                result = self.model.serve([f0, f0_sift, f0_flow])
                result = self.__get_result(result)

                if self.cb != None:
                    print(f"Sending air visibility result: {result}")
                    self.cb(result)
                
    def start(self):
        if self.thread:
            ("Thread already running")
            return

        self.c0.start(0, config.CAMERA_WIDTH, config.CAMERA_HEIGHT, config.CAMERA_FLIP, config.CAMERA_FRAMERATE)
        self.c1.start(1, config.CAMERA_WIDTH, config.CAMERA_HEIGHT, config.CAMERA_FLIP, config.CAMERA_FRAMERATE)
        
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
        self.frame = cv.resize(self.frame, (config.OUTPUT_WIDTH, config.OUTPUT_HEIGHT))

        self.frame_next = cv.imread(frame_next_path)
        self.frame_next = cv.resize(self.frame_next, (config.OUTPUT_WIDTH, config.OUTPUT_HEIGHT))

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
