#!/usr/bin/env python
# Required: python-serial

import serial

class Matrix8x8USB(object):
    '''Object to control display'''
    def __init__(self, tty = '/dev/ttyUSB0', boudrate = 19200):
        self._available_commands = ['clear', 'init', 'tuner', 'symbols']
        self._c = serial.Serial(tty, boudrate, timeout=1.0)
        # TODO: Automatically build & upload firmware

    # Commands:
    def clear(self):
        self._c.write(b'c')

    def init(self):
        self._c.write(b'i')

    def tuner(self, value = 0, info = ''):
        '''Tuner function makes possible to display string tune
        info (2 max): note symbols [Ab,A,Bb,B,C,Db,D,Eb,E,F,Gb,G]
        value: -100..100
        '''
        info = str(info) if info != '' else ''
        value = -100 if value < -100 else (100 if value > 100 else value)
        value = value if value >= 0 else 255+value
        self._c.write(b't%c%s' % (chr(value), info))

    def symbols(self, symbols = '', color = '\xff\xff\xff'):
        '''Symbols function just display color string animation
        symbols (255 max): string of ascii symbols
        color: 3 byte RGB string
        '''
        symbols = str(symbols) if symbols != '' else ''
        if len(color) != 3:
            color = "\xff\x00\x00"
        self._c.write(b's%c%c%c%s' % (color[0], color[1], color[2], symbols))

if __name__ == '__main__':
    import time
    display = Matrix8x8USB("/dev/ttyUSB0")

    #display.symbols("1 3 5 7 9 11 14 17 20 23 26 29 32 35 38 41 44 47 50 53 56 59 62 65 68 71 74 77 80 83 86 89 92 95 98 101 105 109 113 117 121 125 129 133 137 141 145 149 153 157 161 165 169 173 177 181 185 189 193 197 201 205 209 213 217 221 225 229 233 237 241 245 249 253...", "\x00\x55\x00")

    try:
        while True:
            display.tuner(-100, 'C')
            time.sleep(0.1)
            display.tuner(-80, 'Db')
            time.sleep(0.1)
            display.tuner(-60, 'D')
            time.sleep(0.1)
            display.tuner(-40, 'Eb')
            time.sleep(0.1)
            display.tuner(-20, 'E')
            time.sleep(0.1)
            display.tuner(0, 'F')
            time.sleep(0.1)
            display.tuner(1, 'Gb')
            time.sleep(0.1)
            display.tuner(15, 'G')
            time.sleep(0.1)
            display.tuner(25, 'Ab')
            time.sleep(0.1)
            display.tuner(46, 'A')
            time.sleep(0.1)
            display.tuner(98, 'Bb')
            time.sleep(0.1)
            display.tuner(100, 'B')
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        print('Exiting')
    except:
        print('Abnormal exiting')
        raise
