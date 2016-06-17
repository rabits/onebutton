// Color functions to adjust brightness
#ifndef COLOR_H
#define COLOR_H

#define MIN3(x,y,z)  ((y) <= (z) ? \
                         ((x) <= (y) ? (x) : (y)) \
                     : \
                         ((x) <= (z) ? (x) : (z)))

#define MAX3(x,y,z)  ((y) >= (z) ? \
                         ((x) >= (y) ? (x) : (y)) \
                     : \
                         ((x) >= (z) ? (x) : (z)))

// TODO: floating point is used - switch to integer to increase performance
void rgb2hsv(uint8_t rgb[], float hsv[]) {
    float rd = rgb[0]/255.0f;
    float gd = rgb[1]/255.0f;
    float bd = rgb[2]/255.0f;
    float max = MAX3(rd, gd, bd),
          min = MIN3(rd, gd, bd);
    float h, s, v = max;
    float d = max - min;

    s = max == 0 ? 0 : d / max;

    if( max == min ) { 
        h = 0; // achromatic
    } else {
        if( max == rd ) {
            h = (gd - bd) / d + (gd < bd ? 6 : 0);
        } else if( max == gd ) {
            h = (bd - rd) / d + 2;
        } else if( max == bd ) {
            h = (rd - gd) / d + 4;
        }
        h /= 6;
    }

    hsv[0] = h;
    hsv[1] = s;
    hsv[2] = v;
}

// TODO: floating point is used - switch to integer to increase performance
void hsv2rgb(float hsv[], uint8_t rgb[]) {
    float r,g,b;
    int i = int(hsv[0] * 6);
    float f = hsv[0] * 6 - i;
    float p = hsv[2] * (1 - hsv[1]);
    float q = hsv[2] * (1 - f * hsv[1]);
    float t = hsv[2] * (1 - (1 - f) * hsv[1]);

    switch( i % 6 ){
        case 0: r = hsv[2], g = t, b = p; break;
        case 1: r = q, g = hsv[2], b = p; break;
        case 2: r = p, g = hsv[2], b = t; break;
        case 3: r = p, g = q, b = hsv[2]; break;
        case 4: r = t, g = p, b = hsv[2]; break;
        case 5: r = hsv[2], g = p, b = q; break;
    }

    rgb[0] = r * 255;
    rgb[1] = g * 255;
    rgb[2] = b * 255;
}

void bright(uint8_t rgb[], uint8_t brightness) {
    float hsv[] = {0.0f, 0.0f, 0.0f};
    rgb2hsv(rgb, hsv);
    hsv[2] = hsv[2]*brightness/255;
    hsv2rgb(hsv, rgb);
}

#endif // COLOR_H
