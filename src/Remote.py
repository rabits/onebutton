#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import subprocess
from threading import Thread

from jsonrpctcp.server import Server

import Log as log
from Module import Module

# Decorator for jsonrpc functions
def jsonrpc(ns = None):
    def func_dec(func):
        func._jsonrpc = ns
        return func
    return func_dec


class Remote(Module):
    """Remote module - make possible to control OneButton through json-rpc"""

    def __init__(self, **kwargs):
        Module.__init__(self, **kwargs)

        self._server = Server((self._cfg.get('address', ''), self._cfg.get('port', 9000)))

        self._registerHandlers()

        self._server_proc = Thread(target=self._server.serve)
        self._server_proc.daemon = True
        self._server_proc.start()

    def _exec(self, cmd):
        return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=self._logerr).communicate()[0]

    def _registerHandlers(self):
        functions = self.list()
        for name, f in functions.items():
            log.debug("Remote: add handler for %s - %s" % (f['function'], name))
            self._server.add_handler(getattr(self, name), f['function'])

    def stop(self):
        log.info("Stopping '%s'" % self._cfg.get('name', '[unknown Remote]'))
        self._server.shutdown()

    # Remote jsonrpc functions
    @jsonrpc()
    def version(self):
        return self._control.version()

    @jsonrpc()
    def list(self):
        out = {}
        functions = [getattr(self, f) for f in dir(self) if callable(getattr(self, f)) and hasattr(getattr(self, f), '_jsonrpc')]
        for f in functions:
            name = '%s.%s' % (f._jsonrpc, f.__name__) if f._jsonrpc else f.__name__
            args = [a for a in f.__code__.co_varnames if a != 'self']
            out[f.__name__] = {'function': name, 'arguments': args}
        return out

    @jsonrpc('system')
    def poweroff(self):
        log.info("Remote: poweroff")
        return self._exec(['sudo', 'poweroff'])

    @jsonrpc('system')
    def reboot(self):
        log.info("Remote: reboot")
        return self._exec(['sudo', 'reboot'])

    @jsonrpc('onebutton')
    def upgrade(self):
        log.info("Remote: upgrade")
        return 'TODO: upgrade'

    @jsonrpc('onebutton')
    def restart(self):
        log.info("Remote: restart")
        return self._control.stop()

    @jsonrpc('audio')
    def volumeIn(self, dev = None, left = None, right = None):
        log.info("Remote: volumeIn dev:%s l:%d r:%d" % (dev, left, right))
        # TODO: get & set
        return [0, 0]

    @jsonrpc('audio')
    def volumeOut(self, dev = None, left = None, right = None):
        log.info("Remote: volumeOut dev:%s l:%d r:%d" % (dev, left, right))
        # TODO: get & set
        return [0, 0]
