#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import Log as log
from Process import Process
#from Plugin import Plugin

class Display(Process):
    """Display controller - interface to show some info"""

    def stop(self):
        log.info("Stopping '%s'" % self._cfg.get('name', '[unknown Display]'))
        Process.stop(self)
