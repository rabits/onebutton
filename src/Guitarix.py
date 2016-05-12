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
