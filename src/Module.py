#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import Log as log

class Module(object):
    """Module - basic module class"""
    def __init__(self, config, logout, logerr):
        self._cfg = config
        self._logout = logout
        self._logerr = logerr

    def wait(self):
        pass

    def stop(self):
        log.info("Stopping %s instance" % self.__class__.__name__)
