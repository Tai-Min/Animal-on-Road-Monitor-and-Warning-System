#pragma once
#include "signs/animals_sign.h"
#include "signs/wild_animals_sign.h"
#include "signs/speed_sign.h"
#include "signs/stop_sign.h"
#include "signs/hackster_logo.h"
#include "signs/taimin.h"

template <class Drawer>
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
     * @brief
     *
     * @param drawer
     * @param panel_height_pixels
     * @param index
     */
    Sign(Drawer &drawer, unsigned int offset_y, uint8_t panel_width, uint8_t panel_height, uint8_t font_height)
        : m_drawer(drawer),
          m_offset_y(offset_y),
          m_panel_width(panel_width),
          m_panel_height(panel_height),
          m_font_height(font_height),
          m_multicolor(2, (uint16_t*)m_textColors)
    {
    }

    char getSpeedFirstDigit(SpeedType speedType)
    {
        switch(speedType)
        {
            case SpeedType::SPEED_30:
            return '3';
            case SpeedType::SPEED_50:
            return '5';
            case SpeedType::SPEED_70:
            return '7';
            case SpeedType::SPEED_90:
            return '9';
        }
        return '0';
    }

    void setSign(SignType signType, SpeedType speedType = SpeedType::SPEED_30)
    {
        char str[] = "0 0";
        uint16_t width = 0;

        switch (signType)
        {
        case SignType::TAIMIN:
            m_drawer.drawRGBBitmap(0, m_offset_y, (const uint16_t *)taimin.pixel_data, taimin.width, taimin.height);
            break;
        case SignType::LOGO_HACKSTER:
            m_drawer.drawRGBBitmap(0, m_offset_y, (const uint16_t *)hackster_logo.pixel_data, hackster_logo.width, hackster_logo.height);
            break;
        case SignType::SIGN_ANIMALS:
            m_drawer.drawRGBBitmap(0, m_offset_y, (const uint16_t *)animals_sign.pixel_data, animals_sign.width, animals_sign.height);
            break;
        case SignType::SIGN_WILD_ANIMALS:
            m_drawer.drawRGBBitmap(0, m_offset_y, (const uint16_t *)wild_animals_sign.pixel_data, wild_animals_sign.width, wild_animals_sign.height);
            break;
        case SignType::SIGN_STOP:
            m_drawer.drawRGBBitmap(0, m_offset_y, (const uint16_t *)stop_sign.pixel_data, stop_sign.width, stop_sign.height);
            break;
        case SignType::SIGN_SPEED:
            m_drawer.drawRGBBitmap(0, m_offset_y, (const uint16_t *)speed_sign.pixel_data, speed_sign.width, speed_sign.height);

            str[0] = getSpeedFirstDigit(speedType);
            width = m_drawer.stringWidth(str, 3);
            m_drawer.drawStringX((m_panel_width - width) / 2, m_offset_y + (m_panel_height - m_font_height) / 2, str, &m_multicolor, 0);
            break;
        default:
            break;
        }
    }

private:
    Drawer &m_drawer;
    unsigned int m_offset_y;
    uint8_t m_panel_width;
    uint8_t m_panel_height;
    uint8_t m_font_height;

    const uint16_t m_textColors[2] = {0xFFFF, 0};
    DMD_Colorlist m_multicolor;
};