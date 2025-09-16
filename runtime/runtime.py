import signal
import sys
import time
import os
import config
from animal_classifier.mqtt_runner import MQTT_Runner
from animal_classifier.second_stage_animal_classifier import SecondStageClassifier
from animal_classifier import secrets
from air_visibility.camera import Camera
from air_visibility.air_visibility_runner import AirVisibilityRunner
from sign_driver.sign_driver import SignDriver
from runtime_logic import RuntimeLogic

if __name__ == "__main__":
    second_stage_classifier = None
    mqtt_runner = None
    air_visibility_runner = None
    sign_logic = None

    def sigint_handler(signal, frame):
        if mqtt_runner:
            mqtt_runner.stop_runner()
        if second_stage_classifier:
            second_stage_classifier.stop()
        if air_visibility_runner:
            air_visibility_runner.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, sigint_handler)

    sign_logic = RuntimeLogic()

    second_stage_classifier = SecondStageClassifier(os.path.join(os.path.dirname(__file__), "animal_classifier/model/"), sign_logic.animal_classifier_consumer)
    mqtt_runner = MQTT_Runner(secrets.BROKER_IP, secrets.BROKER_PORT, 60, second_stage_classifier.add_animal_detection_to_queue)

    c0 = Camera()
    c1 = Camera()
    air_visibility_runner = AirVisibilityRunner(os.path.join(os.path.dirname(__file__), "air_visibility/model/"), sign_logic.fog_visibility_consumer, c0, c1)

    second_stage_classifier.start()
    mqtt_runner.start_runner()
    air_visibility_runner.start()

    sign_driver = SignDriver(config.SIGN_DRIVER_COM_PORT, 1)

    sign_driver.sign_warning_off()
    sign_driver.sign_speed(SignDriver.SPEED_30)
    
    while True:
        res = sign_logic.loop_iteration()
        
        warning = res[1]
        speed = res[0]
        
        if warning == None:
            sign_driver.sign_warning_off()
        elif warning == SignDriver.SIGN_ANIMALS:
            sign_driver.sign_warning_animals()
        elif warning == SignDriver.SIGN_WILD_ANIMALS:
            sign_driver.sign_warning_wild_animals()

        sign_driver.sign_speed(speed)

        time.sleep(5)