#pragma once
#include <DMD_STM32a.h>
#include "signs/animals_sign.h"
#include "signs/wild_animals_sign.h"
#include "signs/speed_sign.h"
#include "signs/stop_sign.h"
#include "signs/hackster_logo.h"
#include "signs/taimin.h"

class Sign
{
public:
    enum SignType
    {
        TAIMIN,
        LOGO_HACKSTER,
        SIGN_ANIMALS,
        SIGN_WILD_ANIMALS,
        SIGN_SPEED,
        SIGN_STOP
    };

    enum SpeedType
    {
        SPEED_30 = 30,
        SPEED_50 = 50,
        SPEED_70 = 70,
        SPEED_90 = 90
    };

    /**
     * @brief Class constructor
     *
     * @param dmd DMD LED panel driver to use
     * @param offset_y Sign offset in Y in pixels
     * @param panel_width Panel width
     * @param panel_height Panel height
     * @param font_height Font height for speed values
     */
    Sign(DMD &dmd, unsigned int offset_y, uint8_t panel_width, uint8_t panel_height, uint8_t font_height);

    /**
     * @brief Get first digit of speed value
     * 
     * @param speed Speed
     * 
     * @return Digit as a char
     */
    char getSpeedFirstDigit(SpeedType speed);

    /**
     * @brief Draw sign on LED panel
     * 
     * @param signType Sign type to draw
     * @param speed Speed for SIGN_SPEED type
     */
    void drawSign(SignType signType, SpeedType speed = SpeedType::SPEED_30);

    void clear();

private:
    DMD &m_dmd;
    unsigned int m_offset_y;
    uint8_t m_panel_width;
    uint8_t m_panel_height;
    uint8_t m_font_height;

    const uint16_t m_textColors[2] = {0xFFFF, 0};
    DMD_Colorlist m_multicolor;
};