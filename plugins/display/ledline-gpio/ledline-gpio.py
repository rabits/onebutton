#!/usr/bin/env python

import wiringpi2 as wpi
import threading, time
import socket
from math import ceil

class ServerThread(threading.Thread):
    '''Create input connection & process connections'''
    def __init__(self, host, port, process_func):
        threading.Thread.__init__(self)
        self.setDaemon(True)

        (self._hostport, self._process) = ((host, port), process_func)

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind(self._hostport)
        self._sock.listen(1)

    def run(self):
        self._exit = False
        while True:
            print "Listening on %s:%d" % self._hostport
            (conn, addr) = self._sock.accept()
            if self._exit:
                break

            print "Connection from:", addr

            cmd = None
            data = ''
            while True:
                buf = conn.recv(1024)
                if not buf:
                    break
                if not cmd:
                    cmd = buf.strip()
                else:
                    data += buf
            conn.close()
            self._process(cmd, data)

    def stop(self):
        self._exit = True
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(self._hostport)
        self._sock.close()

class LedLineGPIO(threading.Thread):
    '''Object to control display'''
    def __init__(self, pins):
        threading.Thread.__init__(self)
        self.setDaemon(True)

        self._available_commands = ['clear', 'tuner']

        self._pins = pins

        wpi.wiringPiSetup()
        for pin in self._pins:
            wpi.pinMode(pin, wpi.GPIO.OUTPUT)

        self._delay = None

        self.clear()
        self._setDelay(0.01)

    def _setBuffer(self, buf, btype):
        self._buffer = buf
        self._bdirty = True
        self._btype = buf

    def _isBType(self, btype):
        return self._btype == btype

    def _isBDirty(self):
        return self._bdirty
    
    def _setDelay(self, seconds):
        if self._delay != seconds:
            self._delay = seconds

    def run(self):
        self._continue = True
        while self._continue:
            self._bdirty = False
            for buf in self._buffer:
                for pin in range(10):
                    wpi.digitalWrite(self._pins[pin], (buf>>pin) & 1)
                
                # Do not using wpi.delayMicroseconds due to not supported threading
                if self._delay > 0.1:
                    for w in range(1, int(ceil(self._delay*10))+1):
                        time.sleep(min(0.1, self._delay - 0.1*w))
                        if self._isBDirty():
                            break
                else:
                    time.sleep(self._delay)

                if self._isBDirty():
                    break

    def command(self, cmd, data = None):
        if cmd in self._available_commands:
            print "Exec '%s'" % cmd
            if data:
                getattr(self, cmd)(data)
            else:
                getattr(self, cmd)()

    def stop(self):
        self._continue = False

    # Commands:
    def clear(self):
        self._setBuffer([0b0000000000], None)

    def tuner(self, value):
        '''Tuner function makes possible to display string tune
        value: -100..100
        '''
        try:
            if isinstance(value, basestring):
                value = int(value.strip())
        except Exception as e:
            print("ERROR: Unable to parse value:", e)
            return

        if value < 0:
            if not self._isBType('tuner<0'):
                data = []
                for i in range(10):
                    data.append(0b0000000000 | 1<<((i+5)%10))
                self._setBuffer(data, 'tuner<0')
            self._setDelay(1.0/abs(value))
        elif value > 0:
            if not self._isBType('tuner>0'):
                data = []
                for i in reversed(range(10)):
                    data.append(0b0000000000 | 1<<((i+5)%10))
                self._setBuffer(data, 'tuner<0')
            self._setDelay(1.0/abs(value))
        else:
            self._setBuffer([0b0000110000, 0b0000000000], 'tuner0')
            self._setDelay(0.5)

if __name__ == '__main__':
    display = LedLineGPIO([7, 0, 2, 1, 4, 5, 6, 3, 23, 24])

    server = ServerThread('localhost', 8080, display.command)

    try:
        server.start()
        display.start()
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        print('Exiting')
        server.stop()
        display.stop()
    except:
        print('Abnormal exiting')
        server.stop()
        display.stop()
        raise
