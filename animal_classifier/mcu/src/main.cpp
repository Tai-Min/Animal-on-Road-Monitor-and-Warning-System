#include <Arduino.h>
#include <esp_camera.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include "pins.h"
#include "secrets.h"
#include "camera_test.h"
#include "classifier.h"
#include "model.h"

bool configureCamera()
{
  Serial.begin(115200);
  Serial.setDebugOutput(true);

  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_RGB565;
  config.frame_size = FRAMESIZE_QVGA;
  config.jpeg_quality = 10;
  config.fb_count = 2;

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK)
  {
    Serial.printf("Camera init failed with error 0x%x", err);
    return false;
  }
  return true;
}

bool configureNetwork()
{
  Serial.print("WiFi connecting");
  WiFi.begin(ssid, password);

  int64_t start = esp_timer_get_time();
  int64_t timeout = 10000;
  while ((WiFi.status() != WL_CONNECTED) && (((esp_timer_get_time() - start) / 1000) < timeout))
  {
    delay(500);
    Serial.print(".");
  }
  Serial.println();

  if (WiFi.status() != WL_CONNECTED)
  {
    Serial.println("Failed to connect to WiFi");
    return false;
  }
  return true;
}

WiFiClient espClient;
PubSubClient client(espClient);
Classifier classifier;

void setup()
{
  if (!configureCamera())
  {
    while (true)
    {
      asm("nop");
    }
  }

  if (!configureNetwork())
  {
    while (true)
    {
      asm("nop");
    }
  }

  Serial.print("Device ready! Use 'http://");
  Serial.print(WiFi.localIP());
  Serial.println("' to connect");

  client.setServer(mqttBroker, mqttPort);

  String client_id = "esp32-client-";
  client_id += String(WiFi.macAddress());
  client.connect(client_id.c_str());
  // startTestServer();

  if (!classifier.begin(model))
  {
    while (true)
    {
      asm("nop");
    }
  }
}

void loop()
{
  client.publish(mqttTopic, "Hi, I'm ESP32 ^^");
  camera_fb_t *fb = esp_camera_fb_get();
  if (nullptr == fb)
  {
    Serial.println("Failed to get frame");
    return;
  }

  // Perform classification

  // Return MQTT result
  // TODO: return rgb image too?
  esp_camera_fb_return(fb);
}