#include "classifier.h"
#include <Arduino.h>

Classifier::Classifier()
{
}

bool Classifier::begin(const uint8_t *model)
{
    m_model = tflite::GetModel(model);

    if (m_model->version() != TFLITE_SCHEMA_VERSION)
    {
        Serial.print("Model provided is schema version not equal to supported version - ");
        Serial.print(m_model->version());
        Serial.print(" : ");
        Serial.println(TFLITE_SCHEMA_VERSION);
        return false;
    }
    static tflite::MicroInterpreter interpreter(m_model, m_resolver, m_tensorArea, (size_t)m_tensorAreaSize, &m_reporter);
    m_interpreter = &interpreter;

    TfLiteStatus allocate_status = m_interpreter->AllocateTensors();
    if (allocate_status != kTfLiteOk) {
        Serial.println("AllocateTensors() failed");
        return false;
    }
    model_input = m_interpreter->input(0);
    Serial.print(" Dims: ");
    Serial.print(model_input->dims->size);
    Serial.print(", ");
    Serial.print(model_input->dims->data[0]);
    Serial.print(", ");
    Serial.print(model_input->dims->data[1]);
    Serial.print(", ");
    Serial.print(model_input->type);
    return true;
}