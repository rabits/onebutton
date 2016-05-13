#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import jack

import Log as log
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
        self.clientDisconnect()
        Process.stop(self)

    def _jack_info_log(msg):
        log.log('INFO', msg, self._logout)

    def _jack_error_log(msg):
        log.log('ERROR', msg, self._logout)

    def _clientConnect(self):
        log.info("Connecting Jack '%s'" % self._cfg['name'])
        jack.set_error_function(lambda msg: None)
        self._client = jack.Client("onebutton", no_start_server=True, servername=self._cfg['name'])
        jack.set_info_function(self._jack_info_log)
        jack.set_error_function(self._jack_error_log)

    def clientDisconnect(self):
        if self._client:
            log.info("Disconnecting Jack '%s'" % self._cfg['name'])
            self._client.close()
            jack.set_info_function(None)
            jack.set_error_function(None)
            del self._client
            self._client = None

    def getConnections(self, port):
        return self._client.get_all_connections(port)

    def getPorts(self, name_pattern="", is_audio=False, is_midi=False,
            is_input=False, is_output=False, is_physical=False,
            can_monitor=False, is_terminal=False):
        return self._client.get_ports(name_pattern, is_audio, is_midi,
            is_input, is_output, is_physical,
            can_monitor, is_terminal)

    def connectPorts(self, source, destination):
        return self._client.connect(source, destination)

    def disconnectPorts(self, source, destination):
        return self._client.disconnect(source, destination)

    def disconnectAllPorts(self):
        for port in self.getPorts(is_output=True):
            log.debug("Disconnecting port %s" % port)
            for conn_port in self.getConnections(port):
                log.debug("  disconnecting with: %s" % conn_port)
                self.disconnectPorts(port, conn_port)

    def triggerBypass(self):
        # TODO: really bad implementation of bypass
        if not hasattr(self, "_bypass"):
            self._bypass = False

        if self._bypass:
            self.disconnectAllPorts()
            self._guitarix.connectJack([self])
        else:
            self.disconnectAllPorts()
            for i in [1,2]:
                outs = self.getPorts(name_pattern="system:capture_%d" % i, is_audio=True, is_output=True)
                ins = self.getPorts(name_pattern="system:playback_%d" % i, is_audio=True, is_input=True)
                self.connectPorts(outs[0], ins[0])

        self._bypass = not self._bypass

