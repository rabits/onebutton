#!/usr/bin/env python
# -*- coding: UTF-8 -*-

'''OneButton v0.1

Author:      Rabit <home@rabits.org>
License:     GPL v3
Description: Floor flexible guitar processor, based on Guitarix
Required:    python2.7, python-cffi
'''

import yaml
import sys
import os
import time

from Log import debug, info, warn, error
from Display import Display
from Jack import Jack
from Guitarix import Guitarix
from Button import Button

class OneButton(object):
    """Main application to run onebutton"""
    def __init__(self, config_path):
        self._running = False
        self._processes = {}
        self._cfg_path = config_path
        self._loadConfig()
        self._checkConfig()

    def _loadConfig(self):
        self._cfg = None
        try:
            with file(os.path.abspath(os.path.expanduser(self._cfg_path)), 'rb') as f:
                self._cfg = yaml.load(f.read())
                info("Using configuration from '%s'" % f.name)
        except IOError:
            warn("Unable to read config file '%s'" % path)

        if self._cfg == None:
            raise Exception("Unable to read configuration")

    def _checkConfig(self):
        self._dir = {}
        for key in self._cfg['global']['dir']:
            self._dir[key] = os.path.abspath(os.path.expanduser(self._cfg['global']['dir'][key]))
            if not os.path.isdir(self._dir[key]):
                info("Make directory '%s'" % self._dir[key])
                os.makedirs(self._dir[key])

    def saveConfig(self):
        pass

    def _runProcesses(self, Class):
        name = Class.__name__
        self._processes[name] = []
        for i, cfg in enumerate(self._cfg[name]):
            self._processes[name].append(Class(cfg,
                file(self._dir['logs']+'/%s_%d.out.log' % (name, i), 'w'),
                file(self._dir['logs']+'/%s_%d.err.log' % (name, i), 'w'),
                self._dir['pids']+'/%s_%d.pid' % (name, i)))

        info("Waiting till %s will be started..." % name)
        for proc in self._processes[name]:
            proc.wait()
        info("%s was started" % name)

    def run(self):
        info('Initializing...')
        try:
            self._runProcesses(Display)
            self._runProcesses(Jack)
            self._runProcesses(Guitarix)
            self._runProcesses(Button)
        except:
            error('Something went wrong...')
            self.stop()
            raise

        info('Initialization done')
        self._running = True
        while self._running:
            try:
                time.sleep(5)
            except (KeyboardInterrupt, SystemExit):
                info('Received stop signal')
                break
            except:
                error('Abnormal stop...')
                self.stop()
                raise
        self.stop()

    def _stopProcesses(self, Class):
        if type(Class) == str:
            name = Class
        else:
            name = Class.__name__

        if name in self._processes:
            for proc in self._processes[name]:
                proc.stop()
            for i in range(len(self._processes[name])):
                del self._processes[name][-1]

            del self._processes[name]

    def stop(self):
        info("Stopping processes...")
        self._running = False
        self._stopProcesses(Button)
        self._stopProcesses(Guitarix)
        self._stopProcesses(Jack)
        self._stopProcesses(Display)

        # Stopping last processes
        for name in self._processes:
            self._stopProcesses(name)

if __name__ == '__main__':
    if os.geteuid() == 0:
        error('Script is running by the root user - it is really dangerous! Please use unprivileged user with sudo access')
        sys.exit(1)

    if len(sys.argv) < 2:
        print("Usage: onebutton <config.yaml>")
        error("No config file argument found")
        sys.exit(1)
    onebutton = OneButton(sys.argv[1])

    onebutton.run()

    info("Exiting...")
    sys.exit(0)
