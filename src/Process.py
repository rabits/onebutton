#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from subprocess import Popen, PIPE
from time import sleep
import os
from signal import SIGTERM, SIGKILL
try:
    from gi.repository import GObject
except ImportError:
    import gobject as GObject

import Log as log
from Module import Module

class Process(Module):
    """Process - common class to run command as continuous subprocess"""
    def __init__(self, **kwargs):
        Module.__init__(self, **kwargs)

        if not hasattr(self, "_command"):
            self._command = None
        if not hasattr(self, "_command_cwd"):
            self._command_cwd = None
        self._process = None
        self._client = None
        self._timer_processcheck = None

        self._pidpath = kwargs.get('pidpath')

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

            self._timer_processcheck = GObject.timeout_add(500, self._processCheckRestart)
        else:
            log.warn("Unable to exec command '%s' to start process %s" % (self._command, self.__class__.__name__))

    def _processCheck(self):
        if self._process:
            if self._process.poll() != None:
                if self._process.returncode == 0:
                    log.debug("  process %d terminated successfully" % self._process.pid)
                elif self._process.returncode > 0:
                    log.warn("  process %d terminated with code %d. Please check log files" % (self._process.pid, self._process.returncode))
                else:
                    log.debug("  process %d terminated by signal %d" % (self._process.pid, -self._process.returncode))
                return False
        else:
            log.error("Unable to check process status for %s - process is not started" % self.__class__.__name__)
            return False

        return True

    def _processCheckRestart(self):
        if not self._processCheck():
            log.error("Process %s exited, I need to restart it" % self.__class__.__name__)
            self.stop()
            self.start()

    def stop(self):
        if self._timer_processcheck:
            GObject.source_remove(self._timer_processcheck)
            self._timer_processcheck = None
        if self._process:
            log.info("Stopping %s instance" % self.__class__.__name__)
            self._clientDisconnect()
            if not self._processCheck():
                return

            try:
                pid = self._process.pid
                self._process.terminate()
                for retry in range(30):
                    if not self._processCheck(): break
                    sleep(0.1)
                if self._processCheck():
                    try:
                        os.kill(pid, SIGKILL)
                        for retry in range(30):
                            if not self._processCheck(): break
                            sleep(0.1)
                    except Exception as e:
                        log.warn("Process %s (pid: %d) killing exception: %s" % (self.__class__.__name__, e))
                    else:
                        with open(self._pidpath, 'w') as f:
                            f.truncate()
                    self._process = None
                else:
                    with open(self._pidpath, 'w') as f:
                        f.truncate()
            except Exception as e:
                log.error("Process %s exception durning stopping process: %s" % e)

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
        except Exception as e:
            log.warn("Process %s terminating exception: %s" % (self.__class__.__name__, e))

        with open(self._pidpath, 'w') as f:
            f.truncate()

    def _clientConnect(self):
        log.warn("Unable to connect client to process %s" % self.__class__.__name__)

    def _clientDisconnect(self):
        if self._client != None:
            del self._client
            self._client = None

    def client(self):
        if self._client:
            log.warn("%s client already connected" % self.__class__.__name__)
        else:
            self._retry = 10
            while self._retry > 0:
                if not self._processCheck():
                    raise log.error("%s process ends before init done" % self.__class__.__name__)

                try:
                    self._clientConnect()
                    break
                except Exception as e:
                    self._clientDisconnect()
                    log.debug("Got exception: %s" % e)
                    log.debug("Retry connection to %s (%d)" % (self.__class__.__name__, self._retry))
                    self._retry -= 1
                    sleep(1)

        if not self._client:
            raise log.error("Unable to connect client to %s" % self.__class__.__name__)

    def wait(self):
        if self._process:
            log.info("Waiting for %s init" % self.__class__.__name__)
            self.client()
        else:
            log.warn("%s process not present" % (self.__class__.__name__))

    def name(self):
        return self._cfg.get('name', '[unknown process]')
