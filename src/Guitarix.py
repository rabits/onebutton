#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from jsonrpctcp import config as JSONRPCConfig, connect as JSONRPCConnect

class Guitarix(object):
    def __init(self, config):
        JSONRPCConfig.append_string = '\n'
        self._connection = JSONRPCConnect('localhost', 8888)

    def version(self):
        return self._connection.getversion()
