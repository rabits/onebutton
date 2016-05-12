#include <wiringPi.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>

#define MAX_BUTTONS 10

void handler(int num);

void button0(void) { handler(0); }
void button1(void) { handler(1); }
void button2(void) { handler(2); }
void button3(void) { handler(3); }
void button4(void) { handler(4); }
void button5(void) { handler(5); }
void button6(void) { handler(6); }
void button7(void) { handler(7); }
void button8(void) { handler(8); }
void button9(void) { handler(9); }

typedef struct {
    int8_t pin;
    uint8_t value;
    void * callback;
    unsigned long lit;
} Button;

Button buttons[MAX_BUTTONS] = {
    { 0, 0, &button0, 0 },
    { 0, 0, &button1, 0 },
    { 0, 0, &button2, 0 },
    { 0, 0, &button3, 0 },
    { 0, 0, &button4, 0 },
    { 0, 0, &button5, 0 },
    { 0, 0, &button6, 0 },
    { 0, 0, &button7, 0 },
    { 0, 0, &button8, 0 },
    { 0, 0, &button9, 0 }
};

void releaseWait(int num) {
    uint8_t val;
    while( 1 ) {
        delay(50);
        val = digitalRead(buttons[num].pin);
        if( val == 1 )
            return;
    }
}

void handler(int num) {
    unsigned long interrupt_time = millis();
    if( interrupt_time - buttons[num].lit > 20 ) {
        if( buttons[num].value == 1 ) {
            buttons[num].value = 0;
            printf("{\"type\":\"button\", \"button\":%d, \"state\":1}\n", buttons[num].pin);
            releaseWait(num);
        } else {
            printf("{\"type\":\"button\", \"button\":%d, \"state\":0}\n", buttons[num].pin);
            buttons[num].value = 1;
        }
    }
    buttons[num].lit = interrupt_time;
}

uint8_t buttons_num = 0;

int main(int argc, char *argv[])
{
    // Disable buffering to quick send messages to onebutton
    setbuf(stdout, NULL);
    setbuf(stderr, NULL);

    printf("{\"type\":\"info\", \"msg\":\"Init...\"}\n");
    uint8_t pin = 27;

    if( argc < 2 ) {
        printf("{\"type\":\"error\", \"msg\":\"Usage: sudo ./button <pin> [pin [pin...]]\"}\n");
        return 1;
    }

    if( wiringPiSetupGpio() < 0 ) {
        printf("{\"type\":\"error\", \"msg\":\"Unable to setup wiringPi\"}\n");
        return 1;
    }

    for( int i=1; i<argc && i<=MAX_BUTTONS; i++ ) {
        pin = atoi(argv[i]);

        buttons[i-1].pin = pin;
        buttons[i-1].value = digitalRead(pin);

        if( wiringPiISR(pin, INT_EDGE_FALLING, buttons[i-1].callback) < 0 ) {
            printf("{\"type\":\"error\", \"msg\":\"Unable to setup ISR for pin %d\"}\n", pin);
            return 1;
        } else
            printf("{\"type\":\"info\", \"msg\":\"Installed interrupt for pin %d\"}\n", pin);

        buttons_num++;
    }
    printf("{\"type\":\"init-done\", \"msg\":\"Init done\"}\n");

    while( 1 ) {
        delay(1000);
    }

    return 0;
}
