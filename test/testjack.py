#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import time

import sys, os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import lib.jack as jack

@jack.set_error_function
def error(msg):
    print('Error:', msg)

client = jack.Client("onebutton", no_start_server=True, servername="esi-ugm96")

if client.status.server_started:
    print('JACK server was started')
else:
    print('JACK server was already running')
if client.status.name_not_unique:
    print('unique client name generated:', client.name)

@client.set_shutdown_callback
def shutdown(status, reason):
    print('JACK shutdown!')
    print('status:', status)
    print('reason:', reason)

@client.set_process_callback
def process(frames):
    assert len(client.inports) == len(client.outports)
    assert frames == client.blocksize
    for i, o in zip(client.inports, client.outports):
        o.get_buffer()[:] = i.get_buffer()

#for number in 1, 2:
#    client.inports.register('input_{0}'.format(number))
#    client.outports.register('output_{0}'.format(number))

try:
    client.activate()
    client.transport_start()
    while True:
#        print("Jack Transport: '%s', Status: '%s'" % (client.transport_query(), client.status))
        print("Jack Transport: '%s', Status: '%s'" % (client.transport_state, client.status))
        time.sleep(1)
finally:
    print("exiting")
    client.deactivate()
    client.close()
