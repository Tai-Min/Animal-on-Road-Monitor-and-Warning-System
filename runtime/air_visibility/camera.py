from threading import Thread, Event, Lock
import cv2 as cv
from . import config

class Camera:
    def __init__(self):
        self.thread_event = Event()
        self.thread = None
        self.mutex = Lock()
        self.frame = None

    def __capture_loop(self):
        while not self.thread_event.is_set():
            ret, frame = self.cam.read()

            if ret:
                frame = cv.resize(frame, (config.OUTPUT_WIDTH, config.OUTPUT_HEIGHT))
                with self.mutex:
                    self.frame = frame

    def start(self, sensor_id, width, height, flip, framerate):
        self.id = sensor_id

        capture_str = f"""nvarguscamerasrc sensor_id={sensor_id} ! video/x-raw(memory:NVMM), width=(int){width},
        height={height}, format=(string)NV12, framerate=(fraction){framerate}/1 ! nvvidconv flip-method={flip} !
        video/x-raw, width={width}, height=(int){height}, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink"""

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
        with self.mutex:
            if self.frame is not None:
                return self.frame.copy()
        return None