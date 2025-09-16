# Animal-on-Road-Monitor-and-Warning-System

TODO: img

Utilize vision based decentralized monitoring system to dynamically adjust traffic rules based on animal presence and road condition.

# Setup
* Create project_config.py based on project_config.py.example, verify network, MQTT credentials as well as MODBUS port
* Run in this directory:
```
python prepare_env.py
```
* Follow setup guides in following folders:
```
- air_visibility
- animal_classifier
    - model_1st_stage
    - mcu
    - model_2nd_stage
- led_sign_mcu
```
* Run Mosquitto MQTT broker with provided mosquitto.conf from this directory:
```
mosquitto -v -c mosquitto.conf
```
* Finally run
```
python runtime.py
```