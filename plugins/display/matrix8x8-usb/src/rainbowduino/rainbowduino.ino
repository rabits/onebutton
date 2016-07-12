/**
 * Onebutton Arduino 8x8 rainbowduino display controller
 * Board: "Duemilanove or Diecimila"
**/

#include "Rainbowduino/Rainbowduino.h"
#include "frames_store.h"
#include "color.h"
#include "font5px.generated.h"

void (*_current_show_function)();

uint8_t _frames_num = 10;
uint16_t _next_frame = 0;
uint16_t _frame_delay = 33;

uint8_t _brightness = 100;

char _show_string[255] = "OneButton loading...";
uint8_t _show_string_rgb[] = {0x00, 0x40, 0x00};
uint8_t _show_string_len = strlen(_show_string);

char _read_buffer[260];
unsigned int _buffer_size = 0;

uint8_t _tuner_direction = 0;

uint8_t drawChar(uint8_t ascii, int16_t pos_x, int16_t pos_y, uint8_t rgb[])
{
    uint16_t pos = 0;
    uint16_t offset = 0;
    uint8_t width = getCharPosFont5px(ascii, &pos, &offset);

    if( width > 0 ) {
        pos_y += FONT5PX_HEIGHT-1;
        uint8_t data = pgm_read_byte(font5px_data + offset+pos/8);
        for( uint8_t bit = 0; bit < FONT5PX_HEIGHT*width; bit++ ) {
            if( (pos+bit) % 8 == 0 )
                data = pgm_read_byte(font5px_data + offset+(pos+bit)/8);
            if( pos_x >= 0 && pos_y >= 0 && pos_x < 8 && pos_y < 8 ) {
                if( (data >> (7-(pos+bit)%8)) & 1 )
                    Rb.setPixelXY(pos_x, pos_y, rgb[0], rgb[1], rgb[2]);
            }
            pos_x++;
            if( bit % width == width-1 ) {
                pos_x -= width;
                pos_y--;
            }
        }
    }

    return width;
}

void showClean() {
    _frame_delay = 1000;
    Rb.blankDisplay();
}

void showInit() {
    displayStoredRGBFrame(_next_frame, _brightness);
    _next_frame = (_next_frame+1)%_frames_num;
}

void showTuner()
{
    uint8_t rgb[] = {0x00, 0xff, 0x00};
    if( _tuner_direction == 0 ) {
        _frame_delay = 100;
        if( _next_frame%2 ) {
            bright(rgb, _brightness);
            Rb.setPixelXY(3, 6, rgb[0], rgb[1], rgb[2]);
            Rb.setPixelXY(3, 7, rgb[0], rgb[1], rgb[2]);
            Rb.setPixelXY(4, 6, rgb[0], rgb[1], rgb[2]);
            Rb.setPixelXY(4, 7, rgb[0], rgb[1], rgb[2]);
        } else {
            Rb.blankDisplay();
        }
        _next_frame = (_next_frame+1)%8;
    } else {
        Rb.blankDisplay();
        float hsv[] = {0.000333333f*_frame_delay/2, 1.0f, _brightness/255.0f};
        hsv2rgb(hsv, rgb);
        Rb.setPixelXY(_next_frame, 6, rgb[0], rgb[1], rgb[2]);
        Rb.setPixelXY(_next_frame, 7, rgb[0], rgb[1], rgb[2]);
        _next_frame = (_next_frame+_tuner_direction)%8;
    }

    if( _show_string_len == 1 ) {
        drawChar(_show_string[0], 3, 0, rgb);
    } else if( _show_string_len == 2 ) {
        drawChar(_show_string[0], 0, 0, rgb);
        drawChar(_show_string[1], 4, 0, rgb);
    }
}

void showString() {
    _frame_delay = 150;
    Rb.blankDisplay();

    uint16_t string_width = 8;
    for( uint8_t charpos = 0; charpos < _show_string_len; charpos++ ) {
        uint8_t w = getCharWidthFont5px(_show_string[charpos]);
        int16_t pos = string_width - _next_frame;

        if( pos < 8 ) {
            if( (pos + w) >= 0 ) {
                drawChar(_show_string[charpos], pos, 0, _show_string_rgb);
            } else if( (charpos + 1) >= _show_string_len ) {
                _next_frame = 0;
            }
        } else
            break;

        string_width = string_width + w + 1;
    }

    _next_frame = _next_frame+1;
}

uint8_t readSerial(uint16_t delay_ms, uint8_t bytes = 64) {
    Serial.setTimeout(delay_ms);
    return Serial.readBytes(_read_buffer, bytes);
}

void setup()
{
    Rb.init();
    Serial.begin(19200);
    _current_show_function = &showString;
}

void loop()
{
    uint16_t enter_time, process_time;

    // Processing operations
    enter_time = millis();
    _current_show_function();
    process_time = millis() - enter_time;

    // Check process time
    if( process_time > _frame_delay ) {
        Serial.print("WARNING: process_time > frame_delay ");
        Serial.print(process_time, DEC);
        Serial.print(" ");
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
                    _current_show_function = &showClean;

                    Serial.println("clean:");
                    return;

                case 'i': // Init
                    _current_show_function = &showInit;

                    Serial.println("init:");
                    return;

                case 't': // Tuner
                    if( _read_buffer[1] != 0 ) {
                        _tuner_direction = _read_buffer[1] / abs(_read_buffer[1]); // -1, 1
                        _frame_delay = 2000/abs(_read_buffer[1]);
                    } else
                        _tuner_direction = 0;

                    _buffer_size = readSerial(_frame_delay-process_time, 2);
                    _show_string_len = _buffer_size;
                    if( _show_string_len > 0 )
                        strncpy(_show_string, _read_buffer, 2);

                    _current_show_function = &showTuner;

                    Serial.print("tuner: ");
                    Serial.println(_read_buffer[1], DEC);
                    return;

                case 's': // Symbols
                    _current_show_function = &showString;
                    _next_frame = 0;

                    _show_string_rgb[0] = _read_buffer[1];
                    _buffer_size = readSerial(_frame_delay-process_time, 2);
                    _show_string_rgb[1] = _read_buffer[0];
                    _show_string_rgb[2] = _read_buffer[1];

                    Serial.print("Time: ");
                    Serial.print(_frame_delay-process_time, DEC);
                    Serial.print(" ");
                    _buffer_size = readSerial(_frame_delay-process_time, 255);
                    strncpy(_show_string, _read_buffer, 255);
                    _show_string_len = _buffer_size;
                    Serial.print(_frame_delay-process_time, DEC);

                    Serial.print(" Symbols: '");
                    Serial.print(_show_string);
                    Serial.println("'");
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
