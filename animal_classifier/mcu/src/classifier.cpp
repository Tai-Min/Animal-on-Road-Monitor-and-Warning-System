#include "classifier.h"
#include <Arduino.h>
#include <edge-impulse-sdk/classifier/ei_run_classifier.h>

ClassificationResult runClassifier(DataProcessor rawDataProcessor)
{
    if (!rawDataProcessor)
    {
        return ClassificationResult::ERROR;
    }

    ei_impulse_result_t result = {nullptr};
    signal_t signal;

    signal.total_length = EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE;
    signal.get_data = rawDataProcessor;

    EI_IMPULSE_ERROR res = run_classifier(&signal, &result, false);
    if (res != EI_IMPULSE_OK)
    {
        Serial.println("ERR: Failed to run classifier");
        return ClassificationResult::ERROR;
    }

    return result.classification[0].value > 0.85 ? ClassificationResult::ANIMAL : ClassificationResult::EMPTY;
}