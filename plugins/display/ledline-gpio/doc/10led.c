#include <wiringPi.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char *argv[])
{
    // Pins array
    uint8_t PINS[] = {7, 0, 2, 1, 4, 5, 6, 3, 23, 24};
    int16_t repeats = -1;

    if( argc < 2 ) {
        printf("Usage: sudo ./10led <bytestring> [repeats]\n");
        printf("  0 - led off\n");
        printf("  1 - led on\n");
        printf("  d - delay 10ms\n");
        printf("  f - delay 33.334ms (30 frames/s)\n");
        printf("  s - delay 1s\n");
        return 1;
    }
    if( argc > 2 )
        repeats = atoi(argv[2]);

    uint16_t len = strlen(argv[1]);

    if( wiringPiSetup() < 0 ) {
        printf("Unable to setup wiringPi\n");
        return 1;
    }
    printf("Setup done:");
    for( int pin=0; pin<10; pin++ ) {
        pinMode(PINS[pin], OUTPUT);
        // Clear
        digitalWrite(PINS[pin], 0);
        printf(" %d", PINS[pin]);
    }

    uint8_t buffer_counter = 0;
    uint16_t buffer = 0;

    printf("\nBegin cycle\n");
    
    while( 1 ) {
        for(int i=0; i<len; i++) {
            switch( argv[1][i] ) {
                case '0':
                    buffer &= ~(1<<buffer_counter);
                    buffer_counter++;
                    break;
                case '1':
                    buffer |= 1<<buffer_counter;
                    buffer_counter++;
                    break;
                case 'd':
                    delayMicroseconds(10000);
                    break;
                case 'f':
                    delayMicroseconds(33334);
                    break;
                case 's':
                    delayMicroseconds(1000000);
                    break;
                default:
                    printf("ERROR: unknown byte '%c'\n", argv[1][i]);
                    return 1;
            }
            if( buffer_counter >= 10 ) {
                for( int pin=9; pin>=0; pin-- )
                    digitalWrite(PINS[pin], (buffer>>pin) & 1);
                buffer_counter = 0;
            }
        }

        if( repeats > -1 ) {
            if( repeats > 0 )
                repeats--;
            else
                break;
        }
    }
}
