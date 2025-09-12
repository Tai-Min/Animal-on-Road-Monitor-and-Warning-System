# Building
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