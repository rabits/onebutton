#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import Log as log

class Module(object):
    """Module - basic module class"""
    def __init__(self, **kwargs):
        self._control = kwargs.get('control')
        self._cfg = kwargs.get('config')
        self._logout = kwargs.get('logout')
        self._logerr = kwargs.get('logerr')

    def wait(self):
        pass

    def stop(self):
        log.info("Stopping %s instance" % self.__class__.__name__)
