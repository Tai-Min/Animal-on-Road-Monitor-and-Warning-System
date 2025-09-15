#pragma once
#include <stdint.h>
// constexpr uint64_t DEEP_SLEEP_TIME_US = 10 * 60 * 1000 * 1000; // 10 min
constexpr uint64_t DEEP_SLEEP_TIME_US = 10 * 1000 * 1000; // 10s
const char *MQTT_TOPIC_IMG = "fstStageImg";
const char *MQTT_TOPIC_STDBY = "stdby";
const unsigned long DELAY_AFTER_PUBLISH_MS = 5000;