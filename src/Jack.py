#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from Process import Process

class Jack(Process):
    """Jackd audio controller - one per soundcard"""

    def _prepare(self):
        self._command = ['sleep', '10']
