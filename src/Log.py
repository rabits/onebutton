#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from sys import stderr, stdout, _getframe
from time import strftime, time, localtime
from inspect import stack

# Common using functions:
def debug(msg):
    pass
def info(msg):
    pass
def warn(msg):
    pass
def error(msg):
    pass

# Set verbose level - True: verbose, False: errors only, None: without debug
def logSetVerbose(level):
    global debug, info, warn, error
    if level == True:
        debug = lambda msg: _logOutVerbose('DEBUG', msg)
        info = lambda msg: _logOutVerbose('INFO', msg)
        warn = lambda msg: _logOutVerbose('WARN', msg)
        error = _logErrorVerbose
    elif level == False:
        debug = info = warn = _pass
        error = _logError
    else:
        debug = _pass
        info = lambda msg: _logOut('INFO', msg)
        warn = lambda msg: _logOut('WARN', msg)
        error = _logError

# Mostly service log to use with custom output streams
def log(level, msg, out=stdout):
    out.write('[%s %s]:\t %s\n' % (strftime('%H:%M:%S'), level.upper(), msg))

#
# Service functions
#
def _logOutVerbose(level, msg):
    log_time = time()
    stdout.write('[%s.%s %s, line:%03u]:\t %s\n' % (strftime('%H:%M:%S', localtime(log_time)), str(log_time % 1)[2:8], level, _getframe().f_back.f_lineno, '  ' * (len(stack()) - 1) + msg))

def _logErrorVerbose(msg):
    log_time = time()
    stderr.write('[%s.%s %s, line:%03u]:\t %s\n' % (strftime('%H:%M:%S', localtime(log_time)), str(log_time % 1)[2:8], 'ERROR', _getframe().f_back.f_lineno, '  ' * (len(stack()) - 1) + msg))
    return Exception(msg)

def _logOut(level, msg):
    stdout.write('[%s %s]:\t %s\n' % (strftime('%H:%M:%S'), level, msg))

def _logError(msg):
    stderr.write('[%s %s]:\t %s\n' % (strftime('%H:%M:%S'), 'ERROR', msg))
    return Exception(msg)

def _pass(msg):
    pass

# Init module by setting defaule verbose level
logSetVerbose(None)
