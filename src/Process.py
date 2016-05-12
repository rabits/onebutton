#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from subprocess import Popen, PIPE
from time import sleep
import os
from signal import SIGTERM, SIGKILL

import Log as log

class Process(object):
    """Process - common class to run command as subprocess"""
    def __init__(self, config, logout, logerr, pidpath):
        if not hasattr(self, "_command"):
            self._command = None
        if not hasattr(self, "_command_cwd"):
            self._command_cwd = None
        self._process = None
        self._client = None

        self._cfg = config
        self._logout = logout
        self._logerr = logerr
        self._pidpath = pidpath

        self.start()

    def start(self):
        log.info("Starting %s instance" % self.__class__.__name__)
        if self._command:
            self.stop()
            self._command = [ str(i) for i in self._command ]
            log.debug("Executing %s with logs %s %s" % (self._command,
                self._logout.name if hasattr(self._logout, 'name') else self._logout,
                self._logerr.name if hasattr(self._logerr, 'name') else self._logerr))
            self._process = Popen(self._command, bufsize=1,
                    stdout=self._logout if self._logout else PIPE,
                    stderr=self._logerr if self._logerr else PIPE,
                    cwd=self._command_cwd)
            with open(self._pidpath, 'w') as f:
                f.write(str(self._process.pid))
        else:
            log.warn("Unable to exec command '%s' to start process %s" % (self._command, self.__class__.__name__))

    def stop(self):
        if self._process:
            log.info("Stopping %s instance" % self.__class__.__name__)
            try:
                pid = self._process.pid
                self._process.terminate()
                self._retry = 30
                while self._process.poll() and self._retry > 0:
                    self._retry -= 1
                    sleep(0.1)
                self._process = None
                try:
                    os.kill(pid, 0)
                except:
                    log.warn("Unable to gracefully stop the process %s (pid: %d)" % (self.__class__.__name__, pid))
                else:
                    with open(self._pidpath, 'w') as f:
                        f.truncate()
            except Exception as e:
                log.error("Exception durning stopping process: %s" % e)

        try:
            with open(self._pidpath, 'r') as f:
                pid = f.readline().strip()
                if pid:
                    log.info("Killing %s instance" % self.__class__.__name__)
                    os.kill(int(pid), SIGTERM)
                    log.warn("Terminated process %s pid %s" % (self.__class__.__name__, pid))
                    sleep(5)
                    os.kill(int(pid), SIGKILL)
                    log.warn("Killed process %s pid %s" % (self.__class__.__name__, pid))
        except:
            pass

        with open(self._pidpath, 'w') as f:
            f.truncate()

    def _clientConnect(self):
        log.warn("Unable to connect client to process %s" % self.__class__.__name__)
        pass

    def client(self):
        if self._client:
            log.warn("%s client '%s' already connected" % (self.__class__.__name__, self._cfg['name']))
        else:
            self._retry = 10
            while self._retry > 0:
                try:
                    self._clientConnect()
                    break
                except:
                    self._client = None
                    log.debug("Retry connection to %s (%d)" % (self.__class__.__name__, self._retry))
                    self._retry -= 1
                    sleep(1)

        if not self._client:
            raise log.error("Unable to connect client to %s" % self.__class__.__name__)

    def wait(self):
        if self._process:
            log.info("Waiting for %s init" % self.__class__.__name__)
            self.client()

    def name(self):
        return self._cfg['name']
