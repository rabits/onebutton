#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import time

import Log as log
from Plugin import Plugin

class Button(Plugin):
    """Button controller - runs button plugins and monitor state"""

    def connectJack(self, jack):
        # TODO: temp function
        self._temp_jack = jack

    def processMessage(self, msg):
        # TODO: this is speed change need to be fixed
        if msg['type'] == "button":

            if msg['state'] == 1:
                self._push_time = time.time()
            elif msg['state'] == 0:
                # On release
                if time.time() - self._push_time > 10:
                    import os
                    os.system("sudo poweroff")
                else:
                    if hasattr(self, "_temp_jack"):
                        self._temp_jack.triggerBypass()

    def stop(self):
        log.info("Stopping '%s'" % self._cfg['name'])
        Plugin.stop(self)
