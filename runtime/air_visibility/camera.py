from threading import Thread, Event, Lock
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

if __name__ == "__main__":
    import signal
    import sys
    import time

    camera = None

    def sigint_handler(signal, frame):
        if camera:
            camera.stop()
        sys.exit(0)

    camera_1 = Camera()
    camera_2 = Camera()
    signal.signal(signal.SIGINT, sigint_handler)
    camera_1.start(0, 1280, 720, 2, 30)
    camera_2.start(1, 1280, 720, 2, 30)

    while True:
        f0 = camera_1.get_frame()
        f1 = camera_2.get_frame()

        if f0 is not None and f1 is not None:
            f0 = cv.cvtColor(f0, cv.COLOR_BGR2GRAY)
            f1 = cv.cvtColor(f1, cv.COLOR_BGR2GRAY)
            stereo = cv.StereoBM.create(numDisparities=16, blockSize=25)
            disparity = stereo.compute(f0, f1)
            disp_normalized = None
            disp_normalized = cv.normalize(disparity, disp_normalized, alpha=0, beta=255, norm_type=cv.NORM_MINMAX, dtype=cv.CV_8U)
            
            cv.imshow("camera_0", f0)
            cv.imshow("camera_1", f1)
            cv.imshow("depth", disp_normalized)
            time.sleep(0.1)
            cv.waitKey(1)