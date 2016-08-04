#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import subprocess
import bluetooth as bt

import asyncore
import socket
import uuid

import Log as log
from Module import Module

class Bluetooth(Module):
    """Bluetooth device controller - manage bluetooth device"""

    def __init__(self, config, logerr, logout):
        Module.__init__(self, config, logerr, logout)

        self._proxies = []

        self.setDeviceClass("0xAA040B")
        self.setDeviceName(self._cfg['name'])
        self.setEncryption(self._cfg['encrypt'])
        self.setVisibility(self._cfg['visible'])

        self.proxy('localhost', 8881, 'Guitarix RPC')
        self.proxy('localhost', 8000, 'Guitarix WEB')
        self.proxy('localhost', 9000, 'OneButton')

    def _exec(self, cmd):
        return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=self._logerr).communicate()[0]

    def getDeviceAddress(self):
        log.info("Getting device address '%s'" % self._cfg['dev'])
        out = self._exec(['hcitool', 'dev'])
        olist = out.split()[1:]
        if len(olist) > 1 and self._cfg['dev'] in olist:
            return olist[olist.index(self._cfg['dev'])]
        else
            return None

    def setDeviceClass(self, btclass):
        log.info("Setting device class to '%s'" % btclass)
        self._exec(['sudo', 'hciconfig', self._cfg['dev'], 'class', btclass])

    def setDeviceName(self, name):
        log.info("Setting device name to '%s'" % name)
        self._exec(['sudo', 'hciconfig', self._cfg['dev'], 'name', name])

    def setEncryption(self, val):
        log.info("Setting device encryption to '%s'" % 'encrypt' if val else 'noencrypt')
        self._exec(['sudo', 'hciconfig', self._cfg['dev'], 'encrypt' if val else 'noencrypt'])

    def setVisibility(self, visible):
        log.info("Setting device visibility to '%s'" 'visible' if visible else 'invisible')
        self._exec(['sudo', 'hciconfig', self._cfg['dev'], 'piscan' if visible else 'pscan'])

    def proxy(self, host, port, name):
        self._proxies = ProxyServerBluetooth(host, port, name)


class ProxyClient(asyncore.dispatcher_with_send):
    """Connection to required host & port"""
    def __init__(self, server_client, hostport):
        asyncore.dispatcher_with_send.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect(hostport)
        self._server_client = server_client

    def handle_read(self):
        data = self.recv(8192)
        if data and self._server_client:
            log.debug("> %s" % data)
            self._server_client.send(data)

    def handle_close(self):
        log.debug("Client connection closed")
        self.close()

class ProxyServerClient(asyncore.dispatcher_with_send):
    """Incoming bluetooth connection processor"""
    def __init__(self, sock, hostport):
        self._connection = None
        self._hostport = hostport
        asyncore.dispatcher_with_send.__init__(self, sock)

    def handle_read(self):
        data = self.recv(8192)
        if not self._connection:
            self._connection = ProxyClient(self, self._hostport)
        if data:
            log.debug("< %s" % data)
            self._connection.send(data)

    def handle_close(self):
        log.debug("ServerClient connection closed")
        self.close()
        if self._connection:
            self._connection.close()

class ProxyServerBluetooth(asyncore.dispatcher):
    """Bluetooth connection listener"""
    def __init__(self, host, port, name):
        self._hostport = (host, port)
        self._name = name
        self._handlers = []
        self._bt_uuid = str(uuid.uuid5(uuid.UUID(bytes=b"OneButtonBlueTNS"), name))
        asyncore.dispatcher.__init__(self, sock=bt.BluetoothSocket( bt.RFCOMM ))

        self.bind(("", bt.PORT_ANY))
        self.listen(1)

        bt.advertise_service( self, name,
                              service_id = self._bt_uuid,
                              service_classes = [ self._bt_uuid, bt.SERIAL_PORT_CLASS ],
                              profiles = [ bt.SERIAL_PORT_PROFILE ] )
        log.info("Prepared proxy %s %s" % (name, self._bt_uuid))

    def handle_accept(self):
        client_sock, client_info = self.accept()
        log.debug("%s accepted connection from %s" % (self._name, client_info))
        self._handlers.append(ProxyServerClient(client_sock, self._hostport))
