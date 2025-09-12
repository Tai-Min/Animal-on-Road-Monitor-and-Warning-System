import paho.mqtt.client as mqtt
import numpy as np
from second_stage_animal_classifier import SecondStageClassifier

class MQTT_Runner:
    def __init__(self, ip, port, keepalive, second_stage_classifier : SecondStageClassifier):
        self.ip = ip
        self.port = port
        self.keepalive = keepalive
        self.second_stage_classifier = second_stage_classifier
        self.mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_message = self.on_message

    def start_runner(self):
        self.mqttc.connect(self.ip, self.port, self.keepalive)
        self.mqttc.loop_start()

    def stop_runner(self):
        self.mqttc.loop_stop()

    def on_connect(self, client, userdata, flags, reason_code, properties):
        print(f"Connected with result code {reason_code}")
        client.subscribe("fstStageImg")

    def on_message(self, client, userdata, msg):
        img = np.asarray(bytearray(msg.payload), dtype=np.uint8)
        img.shape = (240, 320, 1)
        self.second_stage_classifier.add_animal_detection_to_queue(img)

    def on_detection(self):
        pass