#include <Arduino.h>
#include <esp_camera.h>
#include "secrets.h"
#include "config.h"
#include "periph.h"
#include "classifier.h"

void setup();
void loop();

/**
 * @brief Enter deep sleep. Called through MQTT callback to mqttTopicStandby
 *
 * @param topic MQTT topic
 * @param msg MQTT message buffer
 * @param length buffer length
 */
static void enterSleep(char *topic, uint8_t *msg, unsigned int length);

/**
 * @brief Edge Impulse input data copier
 */
static int rawDataProcessor(size_t offset, size_t length, float *out_ptr);

/**
 * @brief Publish fb buffer to mqttTopicImg
 *
 * @return false on failure
 */
static bool publishImg();

namespace
{
  WiFiClass *network;
  PubSubClient *mqttClient;
  camera_fb_t *fb;
}

void setup()
{
  configureSerial();

  if (!configureCamera())
  {
    return;
  }

  while (!network)
  {
    network = configureNetwork(secrets::WiFiSSID, secrets::WiFiPassword);
  }

  while (!mqttClient)
  {
    if (!network->isConnected())
    {
      enterRecoveryWiFi();
    }
    mqttClient = configureMQTT(secrets::MQTTBroker, secrets::MQTTPort);
  }

  mqttClient->setCallback(enterSleep);

  if (!mqttClient->subscribe(mqttTopicStandby))
  {
    Serial.println("Failed to subscribe to sleep topic");
    return;
  }

  registerRawDataProcessor(rawDataProcessor);

  Serial.print("Device ready! Use 'http://");
  Serial.print(network->localIP());
  Serial.println("' to connect");
}

void loop()
{
  mqttClient->loop();

  fb = esp_camera_fb_get();
  if (nullptr == fb)
  {
    Serial.println("Failed to get frame");
    return;
  }

  ClassificationResult res = runClassifier();
  if (res == ClassificationResult::ANIMAL)
  {
    if (!publishImg())
    {
      enterRecoveryMQTT(mqttTopicStandby);
    }
  }
  esp_camera_fb_return(fb);
}

void enterSleep(char *topic, uint8_t *msg, unsigned int length)
{
  Serial.println("Entering sleep");
  esp_sleep_enable_timer_wakeup(deepSleepTime_us);
  esp_deep_sleep_start();
}

int rawDataProcessor(size_t offset, size_t length, float *out_ptr)
{
  uint8_t *start = fb->buf + offset;
  for (size_t i = 0; i < length; i++)
  {
    int filled = (start[i] << 16) | (start[i] << 8) | (start[i]);
    out_ptr[i] = filled;
  }
  return 0;
}

bool publishImg()
{
  if (!mqttClient->beginPublish(mqttTopicImg, fb->len, false))
  {
    Serial.println("Failed to begin publish");
    return false;
  }

  mqttClient->write(fb->buf, fb->len);

  if (!mqttClient->endPublish())
  {
    Serial.println("Failed to end publish");
    return false;
  }
  return true;
}
