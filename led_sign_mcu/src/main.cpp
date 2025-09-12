#include <Arduino.h>
#include <DMD_RGB.h>
#include <st_fonts/Arial_Black_16TR.h>
#include "pins.h"
#include "led_panel_config.h"
#include "sign_driver.h"

void enterErrorState();

LED_PANEL ledPanel(muxList, DMD_PIN_nOE, DMD_PIN_LATCH, rgbPins, DISPLAYS_HORIZONTAL, DISPLAYS_VERTICAL, ENABLE_DUAL_BUFFER);
DMD_Standard_Font font((uint8_t *)&Arial_Black_16TR);
uint8_t font_height = ARIAL_BLACK_16TR_HEIGHT;

Sign signs[] = {
    Sign(ledPanel, 0, SINGLE_PANEL_WIDTH, SINGLE_PANEL_HEIGHT, font_height),
    Sign(ledPanel, SINGLE_PANEL_HEIGHT, SINGLE_PANEL_WIDTH, SINGLE_PANEL_HEIGHT, font_height)};

SignDriver<sizeof(signs) / sizeof(signs[0])> signDriver(signs, enterErrorState);

void setup()
{
  ledPanel.init();
  ledPanel.setBrightness(50);
  ledPanel.selectFont(&font);
  ledPanel.setRotation(3);

  Serial.begin(115200);
  Serial.setTimeout(15);

  const Sign::SignType initTypes[] = {Sign::SignType::LOGO_HACKSTER, Sign::SignType::TAIMIN};
  const Sign::SpeedType initSpeeds[] = {Sign::SpeedType::SPEED_30, Sign::SpeedType::SPEED_30};
  signDriver.begin(1, Serial, initTypes, initSpeeds);
  ledPanel.swapBuffers(true);
}

void loop()
{
  signDriver.checkServer();
  ledPanel.swapBuffers(true);
  delay(10);
}

void enterErrorState()
{
  signs[0].drawSign(Sign::SignType::SIGN_WILD_ANIMALS);
  signs[1].drawSign(Sign::SignType::SIGN_SPEED, Sign::SpeedType::SPEED_30);
}