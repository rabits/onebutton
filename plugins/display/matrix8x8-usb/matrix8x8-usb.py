#!/usr/bin/env python
# Required: python-serial

import serial

class Matrix8x8USB(object):
    '''Object to control display'''
    def __init__(self, tty = '/dev/ttyUSB0', boudrate = 19200):

        self._available_commands = ['clear', 'init', 'tuner']

        self._c = serial.Serial(tty, boudrate, timeout=0.1)

    # Commands:
    def clear(self):
        self._c.write(b'c')

    def init(self):
        self._c.write(b'i')

    def tuner(self, info = '', value = 0):
        '''Tuner function makes possible to display string tune
        info (64max): note symbols [Ab,A,Bb,B,C,Db,D,Eb,E,F,Gb,G] (wide string will be scrolled)
        value: -100..100
        '''
        info = str(info) if info != '' else ''
        value = -100 if value < -100 else (100 if value > 100 else value)
        value = value if value >= 0 else 255+value
        self._c.write(b't%c%s' % (chr(value) + info))

if __name__ == '__main__':
    import time
    display = Matrix8x8USB("/dev/ttyUSB0")

    #display.tuner(10)

    try:
    #    server.start()
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        print('Exiting')
        server.stop()
    except:
        print('Abnormal exiting')
        server.stop()
        raise
