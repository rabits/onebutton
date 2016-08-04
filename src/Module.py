#!/usr/bin/env python
# -*- coding: UTF-8 -*-

class Module(object):
    """Module - basic module class"""
    def __init__(self, config, logout, logerr):
        self._cfg = config
        self._logout = logout
        self._logerr = logerr
