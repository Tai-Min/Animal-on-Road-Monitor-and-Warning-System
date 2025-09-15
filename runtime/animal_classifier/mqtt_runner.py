import paho.mqtt.client as mqtt
import numpy as np

class MQTT_Runner:
    def __init__(self, ip, port, keepalive, second_stage_fn):
        self.ip = ip
        self.port = port
        self.keepalive = keepalive
        self.second_stage_fn = second_stage_fn
        self.mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.mqttc.on_connect = self.__on_connect
        self.mqttc.on_message = self.__on_message

    def __on_connect(self, client, userdata, flags, reason_code, properties):
        print(f"Connected with result code {reason_code}")
        client.subscribe("fstStageImg")

    def __on_message(self, client, userdata, msg):
        print(f"Received frame from {client}")
        img = np.asarray(bytearray(msg.payload), dtype=np.uint8)

        if np.prod(img.shape) != 240*320:
            print("Invalid shape received, skipping")
            return
        
        img.shape = (240, 320, 1)

        if self.second_stage_fn:
            self.second_stage_fn(img)
        else:
            print("No 2nd stage fn provided, skipping")

    def start_runner(self):
        self.mqttc.connect(self.ip, self.port, self.keepalive)
        self.mqttc.loop_start()

    def stop_runner(self):
        self.mqttc.loop_stop()

    def send_sleep(self):
        self.mqttc.publish("stdby", "!")


if __name__ == "__main__":
    import signal
    import sys
    import time
    import cv2 as cv

    mqtt_runner = None

    def sigint_handler(signal, frame):
        if mqtt_runner:
            mqtt_runner.stop_runner()
        sys.exit(0)

    signal.signal(signal.SIGINT, sigint_handler)

    def second_stage_fn(img):
        cv.imshow("ESP32", img)
        cv.waitKey(1)
        #cv.destroyAllWindows()

    mqtt_runner = MQTT_Runner("192.168.0.234", 1883, 60, second_stage_fn)
    mqtt_runner.start_runner()

    while True:
        time.sleep(1)