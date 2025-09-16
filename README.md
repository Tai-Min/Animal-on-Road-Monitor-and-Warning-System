# Animal-on-Road-Monitor-and-Warning-System

![alt text](https://github.com/Tai-Min/Animal-on-Road-Monitor-and-Warning-System/blob/cleanup/media/cover.jpg "Controller image")

Utilize vision based decentralized monitoring system to dynamically adjust traffic rules based on animal presence and road condition.

# Setup PC

* Create project_config.py based on project_config.py.example, verify network, MQTT credentials as well as MODBUS port
* Run in this directory:
```
python prepare_env.py
pip install -r ./requirements.txt
```
* Follow setup guides in following folders (from your main PC):
```
- air_visibility
- animal_classifier
    - model_1st_stage
    - mcu
    - model_2nd_stage
- led_sign_mcu
```
* Run Mosquitto MQTT broker with provided mosquitto.conf from this directory*:
```
mosquitto -v -c mosquitto.conf
```

# Setup Jetson Nano
* On Jetson Nano install Python-3.10 using this [guide](https://forums.developer.nvidia.com/t/python-venv-on-jetson-nano/291510)
* Copy this repo (with all work done in previous steps) from your PC to Jetson Nano
* Install the same requirements on Jetson Nano:
```
pip install -r ./requirements.txt
```
* Finally start runtime on Jetson Nano
```
python runtime.py
```

\* mosquitto can be run either from the PC or Jetson Nano, just make sure that both runtime on Jetson and ESP32 have access to the broker.
