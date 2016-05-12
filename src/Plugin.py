#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import json
from threading import Thread

import Log as log
from Process import Process

class Plugin(Process):
    """Plugin - common interface to run plugins"""
    def __init__(self, config, logout, logerr, pidpath):
        log.debug("Initializing plugin %s" % self.__class__.__name__)

        self._init_done = False

        if 'path' in config:
            plugin_runfile = os.path.join(os.path.expanduser(config['plugin_dirpath']), 'run')
        else:
            plugins_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'plugins')
            plugin_runfile = os.path.join(plugins_dir, self.__class__.__name__.lower(), config['type'], 'run')

        if os.path.exists(plugin_runfile):
            self._command_cwd = os.path.dirname(plugin_runfile)
            self._command = [plugin_runfile]
            if 'args' in config['config']:
                self._command += config['config']['args']
        else:
            log.error("Unable to locate plugin executable '%s'" % plugin_runfile)

        Process.__init__(self, config, None, logerr, pidpath)

        self._logout = logout

    def _processStdout(self):
        log.debug("%s: Stdout processing started" % self.__class__.__name__)
        while self._process.poll() is None:
            try:
                line = self._process.stdout.readline()
                message = self._parseMessage(line)
                if not self._processMessageCommonTypes(message):
                    self.processMessage(message)
            except Exception, e:
                log.error("Unable to process message due to error: %s" % str(e))
                log.info("Message: %s" % line.strip())
        log.debug("%s: Stdout processing done" % self.__class__.__name__)

    def _clientConnect(self):
        if not self._process_stdout_thread:
            self._process_stdout_thread = Thread(target=self._processStdout)
            self._process_stdout_thread.daemon = True
            self._process_stdout_thread.start()
        if not self._init_done:
            raise Exception("Init of plugin %s/%s still not done" % (self.__class__.__name__, self._cfg['type']))

        self._client = True

    def _parseMessage(self, data):
        return json.loads(data)

    def _processMessageCommonTypes(self, msg):
        if msg['type'] == 'init-done':
            self._init_done = True
            log.log('INFO', msg['msg'], self._logout)
        elif msg['type'] in ['info', 'warn']:
            log.log(msg['type'], msg['msg'], self._logout)
        elif msg['type']  == 'error':
            log.log(msg['type'], msg['msg'], self._logerr)
        else:
            return False

        return True

    def processMessage(self, msg):
        log.warn("Messages processor not provided for object %s" % self.__class__.__name__)
        log.info("Message: %s" % msg)
        pass
