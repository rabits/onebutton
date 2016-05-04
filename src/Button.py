#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from Log import debug, info, warn, error
from Process import Process

class Button(Process):
    """Button controller - runs button plugins and monitor state"""
