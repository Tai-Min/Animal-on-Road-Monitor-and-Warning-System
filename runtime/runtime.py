import signal
import sys
from animal_classifier.mqtt_runner import MQTT_Runner
from animal_classifier.second_stage_animal_classifier import SecondStageClassifier
from animal_classifier import secrets
import time

if __name__ == "__main__":
    mqtt_runner = None

    def sigint_handler(signal, frame):
        if mqtt_runner:
            mqtt_runner.stop_runner()
        sys.exit(0)

    signal.signal(signal.SIGINT, sigint_handler)

    second_stage_classifier = SecondStageClassifier()
    mqtt_runner = MQTT_Runner(secrets.ip, secrets.port, 60, second_stage_classifier.add_animal_detection_to_queue)
    mqtt_runner.start_runner()

    while True:
        time.sleep(1)
        # Camera feed loop