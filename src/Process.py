#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from subprocess import Popen
from time import sleep
from os import kill
from signal import SIGTERM, SIGKILL

from Log import debug, info, warn, error

class Process(object):
    """Process - common class to run command as subprocess"""
    def __init__(self, config, logout, logerr, pidpath):
        self._command = None
        self._process = None
        self._client = None

        self._cfg = config
        self._logout = logout
        self._logerr = logerr
        self._pidpath = pidpath

        self.start()

    def start(self):
        info("Starting %s instance" % self.__class__.__name__)
        if self._command:
            self.stop()
            self._command = [ str(i) for i in self._command ]
            debug("Executing %s with logs %s %s" % (self._command, self._logout.name, self._logerr.name))
            self._process = Popen(self._command, stdout=self._logout, stderr=self._logerr)
            with open(self._pidpath, 'w') as f:
                f.write(str(self._process.pid))
        else:
            warn("Unable to exec command '%s' to start process %s" % (self._command, self.__class__.__name__))

    def stop(self):
        if self._process:
            info("Stopping %s instance" % self.__class__.__name__)
            try:
                pid = self._process.pid
                self._process.terminate()
                self._retry = 30
                while self._process.poll() and self._retry > 0:
                    self._retry -= 1
                    sleep(0.1)
                self._process = None
                try:
                    kill(pid, 0)
                except:
                    warn("Unable to gracefully stop the process %s (pid: %d)" % (self.__class__.__name__, pid))
                else:
                    with open(self._pidpath, 'w') as f:
                        f.truncate()
            except Exception as e:
                error("Exception durning stopping process: %s" % e)

        try:
            with open(self._pidpath, 'r') as f:
                pid = f.readline().strip()
                if pid:
                    info("Killing %s instance" % self.__class__.__name__)
                    kill(int(pid), SIGTERM)
                    warn("Terminated process %s pid %s" % (self.__class__.__name__, pid))
                    sleep(5)
                    kill(int(pid), SIGKILL)
                    warn("Killed process %s pid %s" % (self.__class__.__name__, pid))
        except:
            pass

        with open(self._pidpath, 'w') as f:
            f.truncate()

    def _clientConnect(self):
        warn("Unable to connect client to process %s" % self.__class__.__name__)
        pass

    def client(self):
        if self._client:
            warn("%s client '%s' already connected" % (self.__class__.__name__, self._cfg['name']))
        else:
            self._retry = 10
            while self._retry > 0:
                try:
                    self._clientConnect()
                    break
                except:
                    self._client = None
                    debug("Retry connection to %s (%d)" % (self.__class__.__name__, self._retry))
                    self._retry -= 1
                    sleep(1)

        if not self._client:
            raise error("Unable to connect client to %s" % self.__class__.__name__)

    def wait(self):
        if self._process:
            info("Waiting for %s init" % self.__class__.__name__)
            self.client()
