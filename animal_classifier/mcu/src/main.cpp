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
 * @brief Publish fb buffer to mqttTopicImg
 *
 * @param fb Frame buffer
 * 
 * @return false on failure
 */
static bool publishImg(camera_fb_t *fb);

namespace
{
  WiFiClass *network;
  PubSubClient *mqttClient;
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
    network = configureNetwork(secrets::WIFI_SSID, secrets::WIFI_PWD);
  }

  while (!mqttClient)
  {
    if (!network->isConnected())
    {
      enterRecoveryWiFi();
    }
    mqttClient = configureMQTT(secrets::MQTT_IP, secrets::MQTT_PORT);
  }

  mqttClient->setCallback(enterSleep);

  if (!mqttClient->subscribe(MQTT_TOPIC_STDBY))
  {
    Serial.println("Failed to subscribe to sleep topic");
    return;
  }

  Serial.print("Device ready! Use 'http://");
  Serial.print(network->localIP());
  Serial.println("' to connect");
}

void loop()
{
  mqttClient->loop();

  camera_fb_t *fb = esp_camera_fb_get();

  if (nullptr == fb)
  {
    Serial.println("Failed to get frame");
    return;
  }

  auto dataProcessor = [fb](size_t offset, size_t length, float *out_ptr) -> int
  {
    uint8_t *start = fb->buf + offset;
    for (size_t i = 0; i < length; i++)
    {
      int filled = (start[i] << 16) | (start[i] << 8) | (start[i]);
      out_ptr[i] = filled;
    }
    return 0;
  };

  ClassificationResult res = runClassifier(dataProcessor);
  if (res == ClassificationResult::ANIMAL)
  {
    if (!publishImg(fb))
    {
      enterRecoveryMQTT(MQTT_TOPIC_STDBY);
    }
    else
    {
      delay(DELAY_AFTER_PUBLISH_MS);
    }
  }
  esp_camera_fb_return(fb);
}

void enterSleep(char *topic, uint8_t *msg, unsigned int length)
{
  Serial.println("Entering sleep");
  esp_sleep_enable_timer_wakeup(DEEP_SLEEP_TIME_US);
  esp_deep_sleep_start();
}

bool publishImg(camera_fb_t *fb)
{
  if (!mqttClient->beginPublish(MQTT_TOPIC_IMG, fb->len, false))
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
