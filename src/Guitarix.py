#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import httplib
from os import path

from jsonrpctcp import config as JSONRPCConfig, connect as JSONRPCConnect
from websockify import WebSocketProxy

import Log as log
from Process import Process

class Guitarix(Process):
    """Guitarix controller"""
    _webprocess = None

    def start(self):
        JSONRPCConfig.append_string = '\n'
        self._command = ['guitarix', '--nogui',
                '--name', self._cfg['name'],
                '--rpcport', self._cfg['rpc_port'],
                '--server-name', self._cfg['jack']]
        Process.start(self)

    def _clientConnect(self):
        log.info("Connecting client '%s'" % self._cfg['name'])
        self._client = JSONRPCConnect('localhost', self._cfg['rpc_port'])
        self.version()

        if self._cfg['web']:
            self._webprocess = GuitarixWeb(self._cfg, self._logout, self._logerr, self._pidpath + '.web.pid')
            self._webprocess.wait()

    def stop(self):
        log.info("Stopping '%s'" % self._cfg['name'])
        if self._webprocess:
            self._webprocess.stop()
            del self._webprocess
        Process.stop(self)

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

class GuitarixWeb(Process):
    """GuitarixWeb UI interface and web proxy
    Unable to use threading or multiprocessing with websockify...
    """

    def start(self):
        base_dir = path.dirname(path.dirname(__file__))
        proxy_path = path.join(base_dir, 'lib', 'websockify', 'websocketproxy.py')
        webui_path = path.join(base_dir, 'guitarix-webui')
        self._command = ['python', '-u', proxy_path,
                '--web', webui_path,
                '*:%d' % self._cfg['web'],
                'localhost:%d' % self._cfg['rpc_port']]
        Process.start(self)

    def _clientConnect(self):
        log.info("Checking GuitarixWeb UI '%s'" % self._cfg['name'])
        self._client = httplib.HTTPConnection('localhost', self._cfg['web'], timeout=10)
        self._client.request('GET', '/')
        r = self._client.getresponse()
        r.close()
        if r.status != 200:
            raise Exception("Unable to connect GuitarWeb UI")

    def stop(self):
        log.info("Stopping web proxy for '%s'" % self._cfg['name'])
        Process.stop(self)
