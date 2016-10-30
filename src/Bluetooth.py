#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import subprocess
from gi.repository import GObject
import dbus
import socket
import uuid

import struct
import zlib

from bluetooth import (Agent, Profile, BUS_NAME, PROFILE_INTERFACE)

import Log as log
from Module import Module

class Bluetooth(Module):
    """Bluetooth device controller - manage bluetooth device"""

    def __init__(self, **kwargs):
        Module.__init__(self, **kwargs)

        self.setState(self._cfg.get('enabled', False))
        self.setDeviceClass("0xAA040B")
        self.setDeviceName(self._cfg.get('name', 'OneButton'))
        self.setEncryption(self._cfg.get('encrypt', True))
        self.setVisibility(self._cfg.get('visible', False))

        self._bus = dbus.SystemBus()

        # Required bluez >= 5.40 due to fix in profiles connections
        self._agent = Agent(self._bus, "/onebutton/agent")
        manager = dbus.Interface(self._bus.get_object(BUS_NAME, "/org/bluez"), "org.bluez.AgentManager1")
        manager.RegisterAgent("/onebutton/agent", "NoInputNoOutput")
        manager.RequestDefaultAgent("/onebutton/agent")

        self._btservice = BTService(self._bus, 'OneButton')

        self.registerService('localhost', 9000, 'OneControl')
        self.registerService('localhost', 8881, 'Guitarix RPC')
        self.registerService('localhost', 8000, 'Guitarix WEB')
        self.registerService('localhost', 22, 'SSH')

    def _exec(self, cmd):
        return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=self._logerr).communicate()[0]

    def getDeviceAddress(self):
        log.info("Getting device address '%s'" % self._cfg.get('dev'))
        out = self._exec(['hcitool', 'dev'])
        olist = out.split()[1:]
        if len(olist) > 1 and self._cfg.get('dev') in olist:
            return olist[olist.index(self._cfg.get('dev'))]
        else:
            return None

    def setState(self, val):
        log.info("Setting device state to '%s'" % 'up' if val else 'down')
        self._exec(['sudo', 'hciconfig', self._cfg.get('dev'), 'up' if val else 'down'])

    def setDeviceClass(self, btclass):
        log.info("Setting device class to '%s'" % btclass)
        self._exec(['sudo', 'hciconfig', self._cfg.get('dev'), 'class', btclass])

    def setDeviceName(self, name):
        log.info("Setting device name to '%s'" % name)
        self._exec(['sudo', 'hciconfig', self._cfg.get('dev'), 'name', name])

    def setEncryption(self, val):
        log.info("Setting device encryption to '%s'" % 'encrypt' if val else 'noencrypt')
        self._exec(['sudo', 'hciconfig', self._cfg.get('dev'), 'encrypt' if val else 'noencrypt'])

    def setVisibility(self, visible):
        log.info("Setting device visibility to '%s'" % 'visible' if visible else 'invisible')
        self._exec(['sudo', 'hciconfig', self._cfg.get('dev'), 'piscan' if visible else 'pscan'])

    def registerService(self, host, port, name):
        self._btservice.registerService(host, port, name)

class ServerSocket:
    """Class to handle server socket and additional data"""
    def __init__(self, handler, service, version, cid):
        log.debug("ServerSocket creating %d to %s" % (cid, service))
        self._handler = handler
        self._version = version
        self._id = cid
        self._service = service
        self._type = None

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        GObject.io_add_watch(self.socket, GObject.IO_IN, self._serverIn)
        GObject.io_add_watch(self.socket, GObject.IO_HUP, self._close)
        self.socket.connect(self._service['hostport'])
        self.socket.setblocking(0)

    def _serverIn(self, ssock, ip_type):
        self._handler._serverIn(self._type, self._id, self.socket)
        try:
            GObject.io_add_watch(self.socket, GObject.IO_IN, self._serverIn)
        except:
            log.debug("ServerSocket %d: already closed" % self._id)

    def _close(self, ssock, ip_type):
        log.debug("ServerSocket %d closed by server" % self._id)
        self._handler.removeServerSocket(self._id)

    def setType(self, itype):
        self._type = itype

    def getServiceId(self):
        return self._service['name']

    def setService(self, service):
        oldhostport = self._service['hostport']
        self._service = service
        if oldhostport != self._service['hostport']:
            self.socket.connect(self._service['hostport'])

    def close(self):
        log.debug("ServerSocket %d closing" % self._id)
        self.socket.close()

class BTHandler:
    """Incoming bluetooth connection processor"""

    # PacketType enum
    TYPE_DATA = 0x00         # Plain data
    TYPE_ZLIB = 0x01         # ZLIB Compressed data
    TYPE_QCOMPRESS = 0x02    # qCompress compressed data

    TYPE_GETSERVICES = 0x10  # Get available services list
    TYPE_GETSERVICE = 0x11   # Get service
    TYPE_SETSERVICE = 0x12   # Set service

    TYPE_SOCKET_CLOSE = 0xff # Socket closed

    def __init__(self, btservice, hid, fd, path):
        log.debug("BTHandler: creating %d for %s" % (hid, path))
        self._btservice = btservice
        self._hid = hid
        self._service_id = None

        self._servers = {}

        self._client_socket = socket.fromfd(fd, socket.AF_UNIX, socket.SOCK_STREAM)
        self._client_socket.setblocking(0)

        GObject.io_add_watch(self._client_socket, GObject.IO_IN, self._clientIn)
        GObject.io_add_watch(self._client_socket, GObject.IO_HUP, self._close)

    def _processInData(self, itype):
        data = self._socketRead(self._client_socket, 5)
        cid, size= struct.unpack('!Bl', data)
        #log.debug("BTHandler: %d Data In header: channel id: %d, data size: %d" % (self._hid, cid, size))

        if size > 0:
            data = self._socketRead(self._client_socket, size)

        server_socket = self._getServerSocket(cid, itype).socket

        data = {
            self.TYPE_DATA:      lambda d: d,
            self.TYPE_ZLIB:      lambda d: zlib.decompress(d),
            self.TYPE_QCOMPRESS: lambda d: zlib.decompress(d[4:]),
        }[itype](data)
        #log.debug("Data: %s" % data)

        self._socket_write(server_socket, data)

    def _processOutData(self, itype, cid, data):
        data = {
            self.TYPE_DATA:      lambda d: d,
            self.TYPE_ZLIB:      lambda d: zlib.compress(d),
            self.TYPE_QCOMPRESS: lambda d: struct.pack('>L', len(data)) + zlib.compress(data),
        }[itype](data)

        header = struct.pack('!Bl', cid, len(data))
        #log.debug("BTHandler: Data Out Header id: %d, size: %d" % (cid, len(data)))

        data = header + data
        self._respond(itype, data)

    def _processGetServices(self, itype):
        services = self._btservice.getServicesList()
        data = "\x00".join(services)
        data = struct.pack('!l', len(data)) + data
        self._respond(itype, data)

    def _processGetService(self, itype):
        data = self._socketRead(self._client_socket, 1)
        cid = struct.unpack('!B', data)[0]

        data = self._servers[cid].getServiceId()
        if data == None:
            data = ''
        data = struct.pack('!BB', len(data), cid) + data
        self._respond(itype, data)

    def _processSetService(self, itype, version):
        data = self._socketRead(self._client_socket, 2)
        cid, length = struct.unpack('!BB', data)

        service_id = self._socketRead(self._client_socket, length)
        self._setServerSocket(version, cid, service_id)

    def _processSocket(self, itype):
        data = self._socketRead(self._client_socket, 1)
        cid = struct.unpack('!B', data)[0]
        if itype == self.TYPE_SOCKET_CLOSE:
            self.removeServerSocket(cid)

    def _clientIn(self, ssock, ip_type):
        #log.debug("BTHandler: %d client->server" % self._hid)

        data = self._socketRead(self._client_socket, 2)
        version, itype = struct.unpack('!BB', data)
        #log.debug("BTHandler: Header: protocol version: %d, type: %d" % (version, itype))

        try:
            {
                self.TYPE_DATA:      self._processInData,
                self.TYPE_ZLIB:      self._processInData,
                self.TYPE_QCOMPRESS: self._processInData,

                self.TYPE_GETSERVICES: self._processGetServices,
                self.TYPE_GETSERVICE:  self._processGetService,
                self.TYPE_SETSERVICE:  lambda t: self._processSetService(t, version),

                self.TYPE_SOCKET_CLOSE: self._processSocket,
            }[itype](itype)
        except Exception as e:
            log.error("BTHandler: exception while processing request: %s" % e)

        GObject.io_add_watch(self._client_socket, GObject.IO_IN, self._clientIn)

        #log.debug("BTHandler: %d client->server done" % (self._hid))

    def removeServerSocket(self, cid):
        log.debug("BTHandler: %d removing server socket %d" % (self._hid, cid))
        self._servers[cid].close()
        del self._servers[cid]

    def _getServerSocket(self, cid, itype):
        if not self._servers.has_key(cid):
            raise log.error("BTHandler: %d unable to find server connection %d" % (self._hid, cid))
        self._servers[cid].setType(itype)
        return self._servers[cid]

    def _setServerSocket(self, version, cid, service_id):
        # TODO: service remove/change processing
        service = self._btservice.getService(service_id)
        if not self._servers.has_key(cid):
            self._servers[cid] = ServerSocket(self, service, version, cid)
        else:
            self._servers[cid].setService(service)

        return self._servers[cid]

    def _serverIn(self, itype, cid, server_socket):
        #log.debug("BTHandler: %d server->client %d" % (self._hid, cid))

        data = ''
        try:
            while True:
                try:
                    adata = server_socket.recv(1024, socket.MSG_DONTWAIT)
                    if not adata: break
                    data += adata
                    #log.debug("BTHandler: %d readed %d bytes" % (self._hid, len(data)))
                    if len(data) >= 4096: break # limit for the buffer
                except Exception as e:
                    if e.errno == 11: # "Resource temporarily unavailable" is ok error
                        break # Will continue to read later
                    else:
                        raise e
        except Exception as e:
            log.warn("BTHandler: %d server socket %d reading exception: %s" % (self._hid, cid, e))

        if len(data) > 0:
            self._processOutData(itype, cid, data)

        #log.debug("BTHandler: %d server->client %d done" % (self._hid, cid))

    def _respond(self, itype, data):
        version = 0
        header = struct.pack('!BB', version, itype)
        data = header+data
        self._socket_write(self._client_socket, data)

    def _socket_write(self, sock, data):
        total = 0
        #log.debug("BTHandler: %d writing %d bytes" % (self._hid, len(data)))
        while len(data) > total:
            try:
                was = sock.send(data[total:])
                if was == 0:
                    log.error("BTHandler: %d socket connection broken while sending" % self._hid)
                total += was
                #log.debug("BTHandler: %d written: %d" % (self._hid, total))
            except Exception as e:
                if e.errno != 11: # Skipping "Resource temporarily unavailable" error
                    log.warn("BTHandler: %d socket writing exception: %s" % (self._hid, e))
                    raise
        #log.debug("BTHandler: %d Write done" % self._hid)

    def _socketRead(self, sock, size):
        data = ""
        #log.debug("BTHandler: %d reading %d bytes" % (self._hid, size))
        while size > 0:
            try:
                adata = sock.recv(size)
                was = len(adata)
                if was == 0:
                    log.error("BTHandler: %d socket connection broken while receiving" % (self._hid))
                size -= was
                data += adata
                #log.debug("BTHandler: %d read %d bytes left" % (self._hid, size))
            except Exception as e:
                if e.errno != 11: # Skipping "Resource temporarily unavailable" error
                    log.warn("BTHandler: %d socket reading exception: %s" % (self._hid, e))
                    raise
        return data

    def _close(self, ssock, ip_type):
        self._btservice.removeHandler(self._hid)

    def close(self):
        if self._hid >= 0:
            hid = self._hid
            self._hid = -1
            for cid in self._servers.keys():
                self.removeServerSocket(cid)
            self._client_socket.close()
            log.debug("BTHandler: %d connection closed" % hid)

class BTService(Profile):
    """Bluetooth connection listener"""

    def __init__(self, bus, name):
        self._bus = bus
        self._path = "/onebutton/service/%s" % ''.join([s for s in name if s.isdigit() or s.isalpha()])
        Profile.__init__(self, self._bus, self._path)

        self._services = {}
        self._handlers = {}

        self._name = name
        self._bt_uuid = str(uuid.uuid5(uuid.UUID(bytes=b"OneButtonBlueTNS"), name))

        self.start()
        log.info("BTService: Prepared bluetooth service %s %s" % (name, self._bt_uuid))

    def registerService(self, host, port, name):
        if self._services.has_key(name):
            log.error("BTService: service %s already registered" % name)
            return
        self._services[name] = {'name': name, 'hostport': (host, port)}

    def getServicesList(self):
        return self._services.keys()

    def getService(self, name):
        if self._services.has_key(name):
            return self._services[name]
        else:
            raise log.error("BTService: unable to find service %s" % name)

    def start(self):
        log.info("BTService: Registering profile %s %s" % (self._name, self._bt_uuid))

        # Current bluez (5.43) set Service after primary uuid
        # - so we need to set it manually through ServiceRecord xml
        opts = {
#            "Service": dbus.String(self._bt_uuid),
#            "Name": dbus.String(self._name),
#            "PSM": dbus.UInt16(3), # RFCOMM PSM
            "AutoConnect": dbus.Boolean(True),
            "RequireAuthentication": dbus.Boolean(True),
            "RequireAuthorization": dbus.Boolean(False),
            "ServiceRecord": dbus.String('''
                <?xml version="1.0" encoding="UTF-8" ?>
                <record>
                    <attribute id="0x0001">
                        <sequence>
                            <uuid value="{uuid}" />
                            <uuid value="0x1101" />
                        </sequence>
                    </attribute>
                    <attribute id="0x0003">
                        <uuid value="{uuid}" />
                    </attribute>
                    <attribute id="0x0004">
                        <sequence>
                            <sequence>
                                <uuid value="0x0100" />
                            </sequence>
                            <sequence>
                                <uuid value="0x0003" />
                                <uint8 value="0x03" />
                            </sequence>
                        </sequence>
                    </attribute>
                    <attribute id="0x0005">
                        <sequence>
                            <uuid value="0x1002" />
                        </sequence>
                    </attribute>
                    <attribute id="0x0009">
                        <sequence>
                            <sequence>
                                <uuid value="0x1101" />
                                <uint16 value="0x0102" />
                            </sequence>
                        </sequence>
                    </attribute>
                    <attribute id="0x0100">
                        <text value="{name}" />
                    </attribute>
                </record>
            '''.format(uuid=self._bt_uuid, name=self._name))
        }

        manager = dbus.Interface(self._bus.get_object(BUS_NAME, "/org/bluez"), "org.bluez.ProfileManager1")
        manager.RegisterProfile(self._path, '1101', opts)

    def unregister(self):
        log.info("BTService: Unregistering profile %s %s" % (self._name, self._bt_uuid))
        manager = dbus.Interface(self._bus.get_object(BUS_NAME, "/org/bluez"), "org.bluez.ProfileManager1")
        manager.UnregisterProfile(self._path)

    def stop(self):
        log.info("BTService: Stopping bluetooth service %s %s" % (self._name, self._bt_uuid))
        self.unregister()
        Profile.stop(self)

    @dbus.service.method(PROFILE_INTERFACE, in_signature="", out_signature="")
    def Release(self):
        log.debug("BTService: release")

    @dbus.service.method(PROFILE_INTERFACE, in_signature="", out_signature="")
    def Cancel(self):
        log.debug("BTService: cancel")

    @dbus.service.method(PROFILE_INTERFACE, in_signature="oha{sv}", out_signature="")
    def NewConnection(self, path, fd, properties):
        log.debug("BTService: new connection to %s (%s)" % (self._name, path))

        hid = 0
        for i in range(0xff+1):
            if not self._handlers.has_key(i):
                hid = i
                break

        self._handlers[hid] = BTHandler(self, hid, fd.take(), path)
        log.debug("BTService: handler created (%d)" % len(self._handlers))

    def removeHandler(self, hid):
        log.info("BTService: %s %s Removing handler %d" % (self._name, self._bt_uuid, hid))
        if self._handlers.has_key(hid):
            self._handlers[hid].close
            del self._handlers[hid]

    @dbus.service.method(PROFILE_INTERFACE, in_signature="o", out_signature="")
    def RequestDisconnection(self, path):
        print("BTService: RequestDisconnection %s" % (path))
