import signal
import sys
from animal_classifier.mqtt_runner import MQTT_Runner
import time

if __name__ == "__main__":
    mqtt_runner = None

    def sigint_handler(signal, frame):
        if mqtt_runner:
            mqtt_runner.stop_runner()
        sys.exit(0)

    signal.signal(signal.SIGINT, sigint_handler)
    mqtt_runner = MQTT_Runner("192.168.0.234", 1883, 60)
    mqtt_runner.start_runner()

    while True:
        time.sleep(1)
        # Camera feed loop