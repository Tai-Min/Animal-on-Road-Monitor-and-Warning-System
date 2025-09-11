#pragma once

#include <tensorflow/lite/micro/micro_interpreter.h>
#include <tensorflow/lite/micro/all_ops_resolver.h>

class TempReporter: public tflite::ErrorReporter
{
  virtual int Report(const char* format, va_list args)
  {
    return 0;
  } 
};

class Classifier
{
public:
    Classifier();
    bool begin(const uint8_t* model);
private:
    const tflite::Model *m_model = nullptr;
    tflite::MicroInterpreter *m_interpreter = nullptr;
    TfLiteTensor *m_model_input = nullptr;

    static const long m_tensorAreaSize = 50 * 1024;
    uint8_t m_tensorArea[m_tensorAreaSize];

    tflite::AllOpsResolver m_resolver;
    TempReporter m_reporter;
    TfLiteTensor* model_input = nullptr;
};