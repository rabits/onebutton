#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from subprocess import Popen

class Process(object):
    """Process - common class to run command as subprocess"""
    def __init__(self, config, logout, logerr):
        self._cfg = config
        self._logout = logout
        self._logerr = logerr

        self._prepare()
        self.start()

    def _prepare(self):
        # Here you can modify object props
        self._command = ['sleep', '5']

    def start(self):
        print("INFO: Starting %s instance" % self.__class__.__name__)
        self._process = Popen(self._command, stdout=self._logout, stderr=self._logerr)

    def stop(self):
        print("INFO: Stopping %s instance" % self.__class__.__name__)
        self._process.terminate()

    def __del__(self):
        print("INFO: waiting for process %s" % self.__class__.__name__)
        self._process.wait()
