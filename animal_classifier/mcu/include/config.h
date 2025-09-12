#pragma once
#include <stdint.h>
// constexpr uint64_t deepSleepTime_us = 10 * 60 * 1000 * 1000; // 10 min
constexpr uint64_t deepSleepTime_us = 10 * 1000 * 1000; // 10s
const char *mqttTopicImg = "fstStageImg";
const char *mqttTopicStandby = "stdby";