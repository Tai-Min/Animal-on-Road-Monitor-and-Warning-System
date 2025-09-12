#include "periph.h"
#include <Arduino.h>
#include "pins.h"

namespace
{
    WiFiClient espClient;
    PubSubClient mqttClient(espClient);
};

void configureSerial()
{
    Serial.begin(115200);
    Serial.setDebugOutput(true);
}

bool configureCamera()
{
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
    config.pixel_format = PIXFORMAT_GRAYSCALE;
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

WiFiClass *configureNetwork(const char *ssid, const char *pwd)
{
    Serial.print("WiFi connecting");
    WiFi.begin(ssid, pwd);

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
        return nullptr;
    }
    return &WiFi;
}

PubSubClient *configureMQTT(const char *broker, uint16_t port)
{
    if (!WiFi.isConnected())
    {
        return nullptr;
    }

    mqttClient.setServer(broker, port);
    mqttClient.setKeepAlive(100);
    String client_id = "esp32-client-";
    client_id += String(WiFi.macAddress());
    if (!mqttClient.connect(client_id.c_str()))
    {
        Serial.println("Failed to connect to MQTT broker");
        return nullptr;
    }
    return &mqttClient;
}

void enterRecoveryWiFi()
{
    while (!WiFi.isConnected())
    {
        WiFi.reconnect();
        sleep(1000);
    }
}

void enterRecoveryMQTT(const char* resubscribeTopic)
{
    if (!WiFi.isConnected())
    {
        enterRecoveryWiFi();
    }

    while (!mqttClient.connected())
    {
        String client_id = "esp32-client-";
        client_id += String(WiFi.macAddress());
        if(mqttClient.connect(client_id.c_str()))
        {
            mqttClient.subscribe(resubscribeTopic);
        }
        // TODO: subscribe
        sleep(1000);
    }
}