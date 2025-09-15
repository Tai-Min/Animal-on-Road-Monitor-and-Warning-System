from threading import Thread, Event, Lock
import numpy as np
import cv2 as cv

class Camera:
    def __init__(self):
        self.thread_event = Event()
        self.thread = None
        self.mutex = Lock()

    def __capture_loop(self):
        while not self.thread_event.is_set():
            ret, frame = self.cam.read()
            print(ret)

    def start(self):
        
        capture_str = f"""nvarguscamerasrc sensor_id={0} ! video/x-raw(memory:NVMM), width=(int){1920},
        height={1080}, format=(string)NV12, framerate=(fraction){30}/1 ! nvvidconv flip-method={0} !
        video/x-raw, width={1920}, height=(int){1080}, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink"""

        self.cam = cv.VideoCapture(capture_str)


        if self.thread:
            print("Thread already running")

        self.thread_event.clear()
        self.thread = Thread(target=self.__capture_loop)
        self.thread.start()

    def stop(self):
        if self.thread:
            self.thread_event.set()
            self.thread.join()
            self.thread = None
        else:
            print("Thread not running, nothing to stop")

    def get_frame(self):
        pass