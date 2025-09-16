# Introduction
This is the firmware for trail cameras that act as a first stage of animal detection.

# Building
* Firstly follow instructions inside ../model_1st_stage/ to generate model (or skip it and use provided animal-binary-classifier.zip in lib/ folder)
* If you generated your model then replace animal-binary-classifier.zip with your own

Before building you must edit 3rd party lib to accept bigger MQTT payloads:
* Find in PubsubClient.cpp / PubSubClient.h method:
```
size_t buildHeader(uint8_t header, uint8_t* buf, uint16_t length)
```
* Replace it with:
```
size_t buildHeader(uint8_t header, uint8_t* buf, size_t length)
```
* Inside this method replace
```
uint16_t len = length;
```
* With:
```
size_t len = length;
```

After that you should be able to build and upload firmware through PlatformIO UI.

TODO: Create fork of PubSubClient