#include <wiringPi.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>

void subInterrupt(void) {
    printf("Event here!\n");
}

int main(int argc, char *argv[])
{
    printf("init\n");
    uint8_t pin = 27;

    if( argc < 2 ) {
        printf("Usage: sudo ./button <pin>\n");
        return 1;
    }
    if( argc > 1 )
        pin = atoi(argv[1]);

    printf("Setup...");
    if( wiringPiSetup() < 0 ) {
        printf("Unable to setup wiringPi\n");
        return 1;
    }
    if( wiringPiISR(pin, INT_EDGE_FALLING, &subInterrupt) < 0 ) {
        printf("Unable to setup ISR\n");
        return 1;
    }
    printf(" done\n");

    while( 1 ) {
        int val = digitalRead(pin);
        printf("loop: %d\n", val);
        delay(1000);
    }

    return 0;
}
