#pragma once
#include <stddef.h>

typedef int(*DataProcessor)(size_t, size_t, float*);

enum ClassificationResult {
    EMPTY,
    ANIMAL,
    ERROR
};

/**
 * @brief Register pointer to preprocessor function for the classifier
 * 
 * @param processor Pointer to preprocessor
 */
void registerRawDataProcessor(DataProcessor processor);

/**
 * @brief Run inference
 */
ClassificationResult runClassifier();