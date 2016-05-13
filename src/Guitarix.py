#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from jsonrpctcp import config as JSONRPCConfig, connect as JSONRPCConnect

import Log as log
from Process import Process

class Guitarix(Process):
    """Guitarix controller"""

    def start(self):
        JSONRPCConfig.append_string = '\n'
        self._command = ['guitarix', '--nogui',
                '--name', self._cfg['name'],
                '--rpcport', self._cfg['rpc_port'],
                '--server-name', self._cfg['jack']]
        Process.start(self)

    def _clientConnect(self):
        log.info("Connecting Guitarix client '%s'" % self._cfg['name'])
        self._client = JSONRPCConnect('localhost', self._cfg['rpc_port'])
        self.version()

    def version(self):
        return self._client.getversion()

    def connectJack(self, jacks):
        log.info("Connecting ports of Guitarix to Jack...")
        jack = filter(lambda j: j.name() == self._cfg['jack'], jacks)[0]

        # TODO: bad way to make bypass working, please rewrite it
        jack._guitarix = self

        m = self._cfg['mapping']

        for i in m['inputs']:
            log.debug("  Connecting my_out:%d to jack_in:%d" %(i['out'], i['in']))
            jack_outs = jack.getPorts(name_pattern='system:capture_%d' % i['out'], is_audio=True, is_output=True)
            log.debug("    Jack output ports: %s" % jack_outs)
            my_ins = jack.getPorts(name_pattern='%s_%s:in_%d' % (self.name(), i['module'], i['in']), is_audio=True, is_input=True)
            log.debug("    My input ports: %s" % my_ins)

            jack.connectPorts(jack_outs[0], my_ins[0])

        for o in m['outputs']:
            log.debug("  Connecting my_out:%d to jack_in:%d" %(o['out'], o['in']))
            my_outs = jack.getPorts(name_pattern='%s_%s:out_%d' % (self.name(), o['module'], o['out']), is_audio=True, is_output=True)
            log.debug("    My output ports: %s" % my_outs)
            jack_ins = jack.getPorts(name_pattern='system:playback_%d' % o['in'], is_audio=True, is_input=True)
            log.debug("    Jack input ports: %s" % jack_ins)

            jack.connectPorts(my_outs[0], jack_ins[0])

        log.debug("  Connecting Guitarix amp to fx...")
        my_outs = jack.getPorts(name_pattern='%s_amp:out_0' % self.name(), is_audio=True, is_output=True)
        my_ins = jack.getPorts(name_pattern='%s_fx:in_0' % self.name(), is_audio=True, is_input=True)
        jack.connectPorts(my_outs[0], my_ins[0])
