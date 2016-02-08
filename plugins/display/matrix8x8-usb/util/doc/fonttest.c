#include <stdio.h>
#include <inttypes.h>

#include <string.h>

#define PROGMEM 
#include "font5px.h"

uint8_t drawChar(uint8_t ascii, uint16_t pos_x, uint16_t pos_y, uint8_t rgb[])
{
    uint16_t pos = 0;
    uint16_t offset = 0;
    uint8_t width = getCharPosFont5px(ascii, &pos, &offset);
    printf("%c %d %d %d\n\n", ascii, width, pos, offset);

    if( width > 0 ) {
        for( uint8_t bit = 0; bit < FONT5PX_HEIGHT*width; bit++ ) {
            uint8_t data = font5px_data[offset+(pos+bit)/8];
            //printf("0x%02x %d ", data, 7-(pos+bit)%8);
            printf("%c", ((data >> (7-(pos+bit)%8)) & 1) ? '*' : ' ');
            if( bit % width == width-1 )
                printf("\n");
        }
    } else
        printf("ERROR: symbol not found\n");

    return width;
}

int main(int argc, char *argv[])
{
    if( argc < 2 ) {
        printf("ERROR: set character to print as argument\n");
        return 1;
    }

    uint8_t rgb[] = {0xff, 0xff, 0xff};
    drawChar(argv[1][0], 0, 0, rgb);
    return 0;
}
