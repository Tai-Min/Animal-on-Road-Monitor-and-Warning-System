#pragma once
#include <stddef.h>
#include <functional>

typedef std::function<int(size_t, size_t, float*)> DataProcessor;

enum ClassificationResult {
    EMPTY,
    ANIMAL,
    ERROR
};

/**
 * @brief Run inference
 * 
 * @param rawDataProcessor Input data processor
 * 
 * @return Result of the classification
 */
ClassificationResult runClassifier(DataProcessor rawDataProcessor);