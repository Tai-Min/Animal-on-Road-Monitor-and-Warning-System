from threading import Thread, Event, Lock
import numpy as np
import cv2 as cv

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
                frame = cv.resize(frame, (400, 240))
                with self.mutex:
                    self.frame = frame

                cv.imshow("camera", frame)
                cv.waitKey(1)

    def start(self, sensor_id, width, height, flip, framerate):
        
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
        pass

if __name__ == "__main__":
    import signal
    import sys

    camera = None

    def sigint_handler(signal, frame):
        if camera:
            camera.stop()
        sys.exit(0)

    camera = Camera()
    signal.signal(signal.SIGINT, sigint_handler)
    camera.start(0, 1280, 720, 2, 30)
