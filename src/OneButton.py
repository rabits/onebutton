#!/usr/bin/env python
# -*- coding: UTF-8 -*-

'''OneButton v0.1

Author:      Rabit <home@rabits.org>
License:     GPL v3
Description: Floor flexible guitar processor, based on Guitarix
Required:    python2.7
'''

import yaml
import sys
import os
import time

from Display import Display
from Jack import Jack
from Button import Button
from Guitarix import Guitarix

class OneButton(object):
    """Main application to run onebutton"""
    def __init__(self, config_paths):
        self._running = False
        self._processes = {}
        self._cfg_paths = config_paths
        self._loadConfig()
        self._checkConfig()

    def _loadConfig(self):
        self._cfg = None
        for path in self._cfg_paths:
            try:
                with file(os.path.abspath(os.path.expanduser(path)), 'rb') as f:
                    self._cfg = yaml.load(f.read())
                    print("INFO: using configuration from '%s'" % f.name)
            except IOError:
                print("WARN: can't open config file '%s'" % path)

        if self._cfg == None:
            print("ERROR: unable to read configuration")
            sys.exit(1)

    def _checkConfig(self):
        self._dir = {}
        for key in self._cfg['global']['dir']:
            self._dir[key] = os.path.abspath(os.path.expanduser(self._cfg['global']['dir'][key]))
            if not os.path.isdir(self._dir[key]):
                print("INFO: Make directory '%s'" % self._dir[key])
                os.makedirs(self._dir[key])

    def saveConfig(self):
        pass

    def _runDisplay(self):
        self._processes['display'] = []

    def _runJack(self):
        self._processes['jack'] = []
        for jack in self._cfg['jacks']:
            logout = file(self._dir['logs']+'/jack_0.out.log', 'w')
            logerr = file(self._dir['logs']+'/jack_0.err.log', 'w')
            self._processes['jack'].append(Jack({'config':''}, logout, logerr))

    def _runGuitarix(self):
        self._processes['guitarix'] = []

    def _runButton(self):
        self._processes['button'] = []

    def run(self):
        print('INFO: Initializing...')
        try:
            self._runDisplay()
            self._runJack()
            self._runGuitarix()
            self._runButton()
        except:
            print('ERROR: Something went wrong...')
            self.stop()
            raise

        print('INFO: Initialization done')
        self._running = True
        while self._running:
            try:
                time.sleep(5)
            except (KeyboardInterrupt, SystemExit):
                print('INFO: Exiting...')
                break
            except:
                print('ERROR: Abnormal exiting...')
                self.stop()
                raise
        self.stop()

        print("INFO: Exiting...")
        sys.exit(0)

    def stop(self):
        print("INFO: Stopping processes...")
        self._running = False
        for name in self._processes:
            for proc in self._processes[name]:
                proc.stop()
            for i in range(len(self._processes[name])):
                del self._processes[name][-1]

if __name__ == '__main__':
    onebutton = OneButton([
        "~/.config/onebutton/config.yaml",
        "/etc/onebutton/config.yaml",
        "config.yaml"
    ])

    onebutton.run()
