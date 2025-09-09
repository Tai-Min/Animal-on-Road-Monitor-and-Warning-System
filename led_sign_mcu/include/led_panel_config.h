#pragma once
#include <DMD_RGB.h>

constexpr uint8_t SINGLE_PANEL_WIDTH = 64;
constexpr uint8_t SINGLE_PANEL_HEIGHT = 64;
typedef DMD_RGB<RGB64x64plainS32, COLOR_4BITS> LED_PANEL;

constexpr uint8_t DISPLAYS_HORIZONTAL = 2;
constexpr uint8_t DISPLAYS_VERTICAL = 1;
constexpr uint8_t ENABLE_DUAL_BUFFER = true;