#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import jack

from Log import debug, info, warn, error
from Process import Process

class Jack(Process):
    """Jackd audio controller - one per soundcard"""

    def start(self):
        self._command = ['jackd', '--name', self._cfg['name']]
        if self._cfg['config']['rtpriority']:
            self._command += ['--realtime',
                '--realtime-priority', int(self._cfg['config']['rtpriority'])]
        else:
            self._command += ['--no-realtime']

        if self._cfg['type'] == 'alsa':
            self._command += ['-dalsa',
                '--device', self._cfg['config']['device'],
                '--rate', self._cfg['config']['samplerate'],
                '--period', self._cfg['config']['buffer'],
                '--nperiods', self._cfg['config']['periods']]

        jack.set_info_function(self._jack_info_log)
        jack.set_error_function(self._jack_error_log)

        Process.start(self)

    def stop(self):
        self.disconnect()
        Process.stop(self)

    def _jack_info_log(msg):
        self._logout.write("INFO: "+msg+"\n")
        self._logout.flush()

    def _jack_error_log(msg):
        self._logerr.write("ERROR: "+msg+"\n")
        self._logerr.flush()

    def _clientConnect(self):
        info("Connecting Jack '%s'" % self._cfg['name'])
        jack.set_error_function(lambda msg: None)
        self._client = jack.Client("onebutton", no_start_server=True, servername=self._cfg['name'])
        jack.set_info_function(self._jack_info_log)
        jack.set_error_function(self._jack_error_log)

    def disconnect(self):
        if self._client:
            info("Disconnecting Jack '%s'" % self._cfg['name'])
            self._client.close()
            jack.set_info_function(None)
            jack.set_error_function(None)
            del self._client
            self._client = None

    def getConnections(self):
        return self._client.get_all_connections()

    def getPorts(self):
        return self._client.get_ports()
