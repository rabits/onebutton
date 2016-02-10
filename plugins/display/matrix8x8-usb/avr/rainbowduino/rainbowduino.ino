/**
 * Onebutton Arduino 8x8 rainbowduino display controller
**/

#include "Rainbowduino/Rainbowduino.h"
#include "frames_store.h"
#include "color.h"

void (*_current_function)();

uint8_t _frames_num = 10;
uint8_t _next_frame = 0;
uint16_t _frame_delay = 33;

uint8_t _brightness = 100;

char _read_buffer[64];
unsigned int _buffer_size = 0;

uint8_t _tuner_direction = 0;

void showClean() {
    _frame_delay = 1000;
    Rb.blankDisplay();
}

void showTuner()
{
    if( _tuner_direction == 0 ) {
        _frame_delay = 100;
        if( _next_frame%2 ) {
          uint8_t rgb[] = {0x00, 0xff, 0x00};
          bright(rgb, _brightness);
          Rb.setPixelXY(3, 5, rgb[0], rgb[1], rgb[2]);
          Rb.setPixelXY(3, 6, rgb[0], rgb[1], rgb[2]);
          Rb.setPixelXY(3, 7, rgb[0], rgb[1], rgb[2]);
          Rb.setPixelXY(4, 5, rgb[0], rgb[1], rgb[2]);
          Rb.setPixelXY(4, 6, rgb[0], rgb[1], rgb[2]);
          Rb.setPixelXY(4, 7, rgb[0], rgb[1], rgb[2]);
        } else {
          Rb.blankDisplay();
        }
        _next_frame = (_next_frame+1)%8;
    } else {
        Rb.blankDisplay();
        float hsv[] = {0.000333333f*_frame_delay/2, 1.0f, _brightness/255.0f};
        uint8_t rgb[] = {0x00, 0x00, 0x00};
        hsv2rgb(hsv, rgb);
        Rb.setPixelXY(_next_frame, 5, rgb[0], rgb[1], rgb[2]);
        Rb.setPixelXY(_next_frame, 6, rgb[0], rgb[1], rgb[2]);
        Rb.setPixelXY(_next_frame, 7, rgb[0], rgb[1], rgb[2]);
        _next_frame = (_next_frame+_tuner_direction)%8;
    }
}

void showInit() {
  displayStoredRGBFrame(_next_frame, _brightness);
  _next_frame = (_next_frame+1)%_frames_num;
}

uint8_t readSerial(uint16_t delay_ms, uint8_t bytes = 64) {
  Serial.setTimeout(delay_ms);
  bytes = Serial.readBytes(_read_buffer, bytes);
}

void setup()
{
  Rb.init();
  Serial.begin(19200);
  _current_function = &showInit;
}

void loop()
{
  uint16_t enter_time, process_time;

  // Processing operations
  enter_time = millis();
  _current_function();
  process_time = millis() - enter_time;

  // Check process time
  if( process_time > _frame_delay ) {
    Serial.print("WARNING: process_time > frame_delay ");
    Serial.print(process_time, DEC);
    Serial.println(_frame_delay, DEC);
  }

  //
  // Process commands from the serial connection
  //
  while( process_time < _frame_delay ) {
    _buffer_size = readSerial(_frame_delay-process_time, 2);
    if( _buffer_size > 0 ) {
      switch( _read_buffer[0] )
      {

        case 'c': // Clean
          _current_function = &showClean;
          return;

        case 'i': // Init
          _current_function = &showInit;
          return;
 
        case 't': // Tuner
          if( _read_buffer[1] != 0 ) {
            _tuner_direction = _read_buffer[1] / abs(_read_buffer[1]); // -1, 1
            _frame_delay = 2000/abs(_read_buffer[1]);
          } else
            _tuner_direction = 0;

          _current_function = &showTuner;

          Serial.print("tuner: ");
          Serial.println(_read_buffer[1], DEC);
          return;

        default: // Print echo
          _read_buffer[_buffer_size] = 0x00;
          Serial.print("readed data: ");
          Serial.println(_read_buffer);
      }
    }
    process_time = millis() - enter_time;
  }
}

