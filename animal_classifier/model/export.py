import numpy as np
import os
import keras
import tensorflow as tf

def convert_tflite_to_header(tflite_path, output_header_path):

    with open(tflite_path, 'rb') as tflite_file:
        tflite_content = tflite_file.read()

    hex_lines = [', '.join([f'0x{byte:02x}' for byte in tflite_content[i:i+12]]) for i in range(0, len(tflite_content), 12)]
    hex_array = ',\n  '.join(hex_lines)

    with open(output_header_path, 'w') as header_file:
        header_file.write('const unsigned char model[] = {\n  ')
        header_file.write(f'{hex_array}\n')
        header_file.write('};\n\n')
    
if __name__ == "__main__":
    model = keras.saving.load_model('./output/model.keras')
    converter  = tf.lite.TFLiteConverter.from_keras_model(model)
    tflite_model = converter.convert()
    with tf.io.gfile.GFile('./output/model.tflite', 'wb') as f:
        f.write(tflite_model)

    tflite_path = './output/model.tflite'
    output_header_path = '../mcu/include/model.h'

    convert_tflite_to_header(tflite_path, output_header_path)