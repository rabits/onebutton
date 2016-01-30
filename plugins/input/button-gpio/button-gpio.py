#!/usr/bin/env python

import buttonmodule
import socket, time
from threading import Timer

class ButtonGPIO(object):
    '''Two mode button object can send commands to server'''
    def __init__(self, host, port, pin, delay_long = None):
        self._hostport = (host, port)
        self._pin = pin
        self._delay = delay_long
        self._delay_num = 0

        self._state = False
        self._state_long = False
        self._count = 0
        buttonmodule.addButton(self._pin, self._callback)

        #self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #self._sock.bind(self._hostport)
        #self._sock.listen(1)

    def _callback(self, value = None):
        # 1 is button default state - to prevent accidentally change state on interference
        self._state = not value
        self._count += 1

        if self._delay != None:
            if not self._state:
                self._cancelLong()
                if not self._state_long:
                    self._sendState()
                self._state_long = False
            else:
                self._startTimer()
        else:
            self._sendState()

    def _cancelLong(self):
        self._delay_timer.cancel()
        self._delay_num = 0;

    def _startTimer(self):
        self._delay_timer = Timer(self._delay[self._delay_num], self._setLong)
        self._delay_timer.setDaemon(True)
        self._delay_timer.start()

    def _setLong(self):
        self._state_long = True
        self._delay_timer.cancel()
        self._sendState()
        if len(self._delay) - 1 > self._delay_num:
            self._delay_num+=1
            self._startTimer()

    def _sendState(self):
        if self._state_long:
            print "Button", self._pin, "long pressed", self._delay_num
        else:
            print "Button", self._pin, "pressed" if self._state else "released"

    def getState(self):
        return self._state

    def getLong(self):
        return self._state_long

if __name__ == '__main__':
    buttonmodule.setup();
    button = ButtonGPIO('localhost', 8080, 26, [0.5, 1.0])
    button = ButtonGPIO('localhost', 8080, 27)

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        print('Exiting')
    except:
        print('Abnormal exiting')
        button.stop()
        raise
