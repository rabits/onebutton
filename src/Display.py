#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import serial

import Log as log

class Display(object):
    '''RGB Matrix 8x8 rainbowduino display'''
    def __init__(self, tty = '/dev/ttyUSB0', boudrate = 19200):
        self._c = serial.Serial(tty, boudrate, timeout=1.0)
        # TODO: test display

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
