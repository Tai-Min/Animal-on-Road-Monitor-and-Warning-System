#pragma once
#include <MSlave.h>
#include "sign.h"

template <uint8_t NumSigns>
class SignDriver
{
public:
    typedef void (*ErrorCallback)();

private:
    struct SignAddrs
    {
        uint16_t on;
        uint16_t type;
        uint16_t speed;
    };

    MSlave<NumSigns, 0, 2 * NumSigns, 0> m_server;
    Sign *m_signs;
    SignAddrs m_signAddrs[NumSigns];
    ErrorCallback m_errorCb;

    bool isValidSignType(uint16_t type)
    {
        if (type == Sign::SignType::TAIMIN ||
            type == Sign::SignType::LOGO_HACKSTER ||
            type == Sign::SignType::SIGN_ANIMALS ||
            type == Sign::SignType::SIGN_WILD_ANIMALS ||
            type == Sign::SignType::SIGN_SPEED ||
            type == Sign::SignType::SIGN_STOP)
        {
            return true;
        }
        return false;
    }

    bool isValidSpeedType(uint16_t type)
    {
        if (type == Sign::SpeedType::SPEED_30 ||
            type == Sign::SpeedType::SPEED_50 ||
            type == Sign::SpeedType::SPEED_70 ||
            type == Sign::SpeedType::SPEED_90)
        {
            return true;
        }
        return false;
    }

    void processSigns()
    {
        for (uint8_t i = 0; i < NumSigns; i++)
        {
            bool on = m_server.digitalRead(COIL, m_signAddrs[i].on);

            if (on)
            {
                uint16_t type = m_server.analogRead(HOLDING_REG, m_signAddrs[i].type);
                uint16_t speed = m_server.analogRead(HOLDING_REG, m_signAddrs[i].speed);

                if (isValidSignType(type) && isValidSpeedType(speed))
                {
                    m_signs[i].drawSign(static_cast<Sign::SignType>(type), static_cast<Sign::SpeedType>(speed));
                }
                else
                {
                    if (m_errorCb)
                    {
                        m_errorCb();
                    }
                }
            }
            else
            {
                m_signs[i].clear();
            }
        }
    }

public:
    SignDriver(Sign *signs, ErrorCallback errorCb)
        : m_signs(signs), m_errorCb(errorCb)
    {
        for (uint8_t i = 0; i < NumSigns; i++)
        {
            m_signAddrs[i].on = i;
            m_signAddrs[i].type = i;
            m_signAddrs[i].speed = i + NumSigns;
        }
    }

    void begin(uint8_t modbusID, HardwareSerial &serial, const Sign::SignType *initTypes, const Sign::SpeedType *initSpeeds)
    {
        m_server.begin(modbusID, serial);

        if (initTypes && initSpeeds)
        {
            for (uint8_t i = 0; i < NumSigns; i++)
            {
                m_signs[i].drawSign(initTypes[i], initSpeeds[i]);
                m_server.digitalWrite(COIL, m_signAddrs[i].on, 1);
                m_server.analogWrite(HOLDING_REG, m_signAddrs[i].type, initTypes[i]);
                m_server.analogWrite(HOLDING_REG, m_signAddrs[i].speed, initSpeeds[i]);
            }
        }
    }

    void checkServer()
    {
        if (m_server.available())
        {
            int result = m_server.read();
            if (result)
            {
                processSigns();
            }
        }
    }
};