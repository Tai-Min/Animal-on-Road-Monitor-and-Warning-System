import os
import project_config

def export_air_visibility_model_config(THIS_DIR):
    AIR_VISIBILITY_MODEL_EXPORT_PATH = os.path.join(THIS_DIR, "air_visibility/config.py")
    print(AIR_VISIBILITY_MODEL_EXPORT_PATH)
    with open(AIR_VISIBILITY_MODEL_EXPORT_PATH, 'w') as config:
        config.write(f"FOG_DENSITY_SMALL_BETA = {str(project_config.FOG_DENSITY_SMALL_BETA)}\n")
        config.write(f"FOG_DENSITY_MEDIUM_BETA = {str(project_config.FOG_DENSITY_MEDIUM_BETA)}\n")
        config.write(f"FOG_DENSITY_HIGH_BETA = {str(project_config.FOG_DENSITY_HIGH_BETA)}\n")

        config.write(f"BETAS = {str(project_config.BETAS)}\n")
        config.write(f"BETAS_STR = {str(project_config.BETAS_STR)}\n")

        config.write(f"RGB_IMG_WIDTH = {str(project_config.RGB_IMG_WIDTH)}\n")
        config.write(f"RGB_IMG_HEIGHT = {str(project_config.RGB_IMG_HEIGHT)}\n")

        config.write(f"SIFT_FLOW_IMG_WIDTH = {str(project_config.SIFT_FLOW_IMG_WIDTH)}\n")
        config.write(f"SIFT_FLOW_IMG_HEIGHT = {str(project_config.SIFT_FLOW_IMG_HEIGHT)}")

def export_animal_classifier_mcu_config(THIS_DIR):
    CLASSIFIER_MCU_EXPORT_PATH = os.path.join(THIS_DIR, "animal_classifier/mcu/include/secrets.h")
    print(CLASSIFIER_MCU_EXPORT_PATH)
    with open(CLASSIFIER_MCU_EXPORT_PATH, 'w') as secrets:
        secrets.write(
f"""#pragma once
#include <stdint.h>

namespace secrets
{{
    const char *WIFI_SSID = "{project_config.WIFI_SSID}";
    const char *WIFI_PWD = "{project_config.WIFI_PWD}";

    const char *MQTT_IP = "{project_config.BROKER_IP}";
    const uint16_t MQTT_PORT = {project_config.BROKER_PORT};
}};
""")

def export_first_stage_config(THIS_DIR):
    FIRST_STAGE_MODEL_EXPORT_PATH = os.path.join(THIS_DIR, "animal_classifier/model_1st_stage/config.py")
    with open(FIRST_STAGE_MODEL_EXPORT_PATH, 'w') as config:
        config.write(f"CAMERA_WIDTH = {project_config.ESP32_CAM_FRAME_WIDTH}\n")
        config.write(f"CAMERA_HEIGHT = {project_config.ESP32_CAM_FRAME_HEIGHT}")

def export_second_stage_config(THIS_DIR):
    SECOND_STAGE_MODEL_EXPORT_PATH = os.path.join(THIS_DIR, "animal_classifier/model_2nd_stage/config.py")
    with open(SECOND_STAGE_MODEL_EXPORT_PATH, 'w') as config:
        config.write(f"CAMERA_WIDTH = {project_config.ESP32_CAM_FRAME_WIDTH}\n")
        config.write(f"CAMERA_HEIGHT = {project_config.ESP32_CAM_FRAME_HEIGHT}")

def export_runtime_air_visibility_config(THIS_DIR):
    AIR_VISIBILITY_RUNTIME_EXPORT_PATH = os.path.join(THIS_DIR, "runtime/air_visibility/config.py")
    with open(AIR_VISIBILITY_RUNTIME_EXPORT_PATH, 'w') as config:
        config.write(f"CAMERA_WIDTH = {project_config.CAMERA_WIDTH}\n")
        config.write(f"CAMERA_HEIGHT = {project_config.CAMERA_HEIGHT}\n")
        config.write(f"CAMERA_FLIP = {project_config.CAMERA_FLIP}\n")
        config.write(f"CAMERA_FRAMERATE = {project_config.CAMERA_FRAMERATE}\n")

        config.write(f"OUTPUT_WIDTH = {project_config.SIFT_FLOW_IMG_WIDTH}\n")
        config.write(f"OUTPUT_HEIGHT = {project_config.SIFT_FLOW_IMG_HEIGHT}\n")

        config.write(f"RGB_WIDTH = {project_config.RGB_IMG_WIDTH}\n")
        config.write(f"RGB_HEIGHT = {project_config.RGB_IMG_HEIGHT}\n")

        config.write(f"SIFT_FLOW_WIDTH = OUTPUT_WIDTH\n")
        config.write(f"SIFT_FLOW_HEIGHT = OUTPUT_HEIGHT")

def export_runtime_animal_classifier_config(THIS_DIR):
    ANIMAL_CLASSIFIER_RUNTIME_EXPORT_PATH = os.path.join(THIS_DIR, "runtime/animal_classifier/config.py")
    with open(ANIMAL_CLASSIFIER_RUNTIME_EXPORT_PATH, 'w') as config:
        config.write(f"FRAME_WIDTH = {project_config.ESP32_CAM_FRAME_WIDTH}\n")
        config.write(f"FRAME_HEIGHT = {project_config.ESP32_CAM_FRAME_HEIGHT}")

    ANIMAL_CLASSIFIER_BROKER_RUNTIME_EXPORT_PATH = os.path.join(THIS_DIR, "runtime/animal_classifier/secrets.py")
    with open(ANIMAL_CLASSIFIER_BROKER_RUNTIME_EXPORT_PATH, 'w') as config:
        config.write(f"BROKER_IP = \"{project_config.BROKER_IP}\"\n")
        config.write(f"BROKER_PORT = {project_config.BROKER_PORT}")

if __name__ == "__main__":
    THIS_DIR = os.path.dirname(__file__)

    #export_air_visibility_model_config(THIS_DIR)
    #export_animal_classifier_mcu_config(THIS_DIR)
    #export_first_stage_config(THIS_DIR)
    #export_second_stage_config(THIS_DIR)
    #export_runtime_air_visibility_config(THIS_DIR)
    #export_runtime_animal_classifier_config(THIS_DIR)
    