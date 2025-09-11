#include <Arduino.h>
#include <DMD_RGB.h>
#include <st_fonts/Arial_Black_16TR.h>
#include "pins.h"
#include "led_panel_config.h"
#include "sign.h"

LED_PANEL ledPanel(muxList, DMD_PIN_nOE, DMD_PIN_LATCH, rgbPins, DISPLAYS_HORIZONTAL, DISPLAYS_VERTICAL, ENABLE_DUAL_BUFFER);
DMD_Standard_Font font((uint8_t *)&Arial_Black_16TR);
uint8_t font_width = ARIAL_BLACK_16TR_WIDTH;
uint8_t font_height = ARIAL_BLACK_16TR_HEIGHT;

Sign<LED_PANEL> top_sign(ledPanel, 0, SINGLE_PANEL_WIDTH, SINGLE_PANEL_HEIGHT, font_height);
Sign<LED_PANEL> bottom_sign(ledPanel, SINGLE_PANEL_HEIGHT, SINGLE_PANEL_WIDTH, SINGLE_PANEL_HEIGHT, font_height);

void setup()
{
  ledPanel.init();
  ledPanel.setBrightness(50);
  ledPanel.selectFont(&font);
  ledPanel.setRotation(3);
}

void loop()
{
  top_sign.setSign(Sign<LED_PANEL>::SignType::SIGN_WILD_ANIMALS);
  bottom_sign.setSign(Sign<LED_PANEL>::SignType::SIGN_SPEED, Sign<LED_PANEL>::SpeedType::SPEED_30);
  ledPanel.swapBuffers(true);
  delay(1200);
  //top_sign.setSign(Sign<LED_PANEL>::SignType::SIGN_ANIMALS);
  //bottom_sign.setSign(Sign<LED_PANEL>::SignType::SIGN_SPEED, Sign<LED_PANEL>::SpeedType::SPEED_50);
  //ledPanel.swapBuffers(true);
  //delay(1200);
}