#pragma once
#include <stdint.h>
#include <esp_camera.h>
#include <WiFi.h>
#include <PubSubClient.h>

/**
 * @brief Configure serial debug output
 */
void configureSerial();

/**
 * @brief Configure camera hardware
 */
bool configureCamera();

/**
 * @brief Configure network connection
 * 
 * @param ssid SSID
 * @param pwd Password
 * 
 * @return nullptr on fail
 */
WiFiClass *configureNetwork(const char *ssid, const char *pwd);

/**
 * @brief Configure connection to MQTT broker
 * 
 * @param broker Broker IP
 * @param port Broker port
 * 
 * @return nullptr on fail
 */
PubSubClient *configureMQTT(const char *broker, uint16_t port);

/**
 * @brief Try to reconnect to wifi. Blocks until success.
 * configureNetwork must be run successfully beforehand.
 */
void enterRecoveryWiFi();

/**
 * @brief Try to reconnect to MQTT broker. Blocks until success.
 * Will try to recover WiFi if necessary.
 * configureNetwork and configureMQTT must be run successfully beforehand.
 */
void enterRecoveryMQTT(const char* resubscribeTopic);