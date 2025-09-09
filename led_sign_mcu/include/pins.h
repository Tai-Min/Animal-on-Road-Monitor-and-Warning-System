#pragma once
#include <stdint.h>

constexpr uint8_t DMD_PIN_A = 0;
constexpr uint8_t DMD_PIN_B = 1;
constexpr uint8_t DMD_PIN_C = 2;
constexpr uint8_t DMD_PIN_D = 3;
constexpr uint8_t DMD_PIN_E = 4;

uint8_t muxList[] = {DMD_PIN_A, DMD_PIN_B, DMD_PIN_C, DMD_PIN_D, DMD_PIN_E};

constexpr uint8_t DMD_PIN_nOE = 26;
constexpr uint8_t DMD_PIN_LATCH = 27;

constexpr uint8_t DMD_PIN_CLK = 5;
constexpr uint8_t DMD_PIN_R0 = 6;
constexpr uint8_t DMD_PIN_G0 = 7;
constexpr uint8_t DMD_PIN_B0 = 8;
constexpr uint8_t DMD_PIN_R1 = 9;
constexpr uint8_t DMD_PIN_G1 = 10;
constexpr uint8_t DMD_PIN_B1 = 11;

uint8_t rgbPins[] = {DMD_PIN_CLK, DMD_PIN_R0, DMD_PIN_G0, DMD_PIN_B0, DMD_PIN_R1, DMD_PIN_G1, DMD_PIN_B1};