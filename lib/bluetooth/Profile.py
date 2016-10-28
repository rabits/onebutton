import dbus.service
import socket
from os import close

from . import BUS_NAME

PROFILE_INTERFACE = '%s.Profile1' % BUS_NAME

class Profile(dbus.service.Object):
    """Implementation of simple loopback interface"""

    def __init__(self, bus, object_path):
        dbus.service.Object.__init__(self, bus, object_path)

    @dbus.service.method(PROFILE_INTERFACE, in_signature="", out_signature="")
    def Release(self):
        pass

    @dbus.service.method(PROFILE_INTERFACE, in_signature="", out_signature="")
    def Cancel(self):
        pass

    @dbus.service.method(PROFILE_INTERFACE, in_signature="oha{sv}", out_signature="")
    def NewConnection(self, path, fd, properties):
        self._fd = fd.take()

        server_sock = socket.fromfd(self._fd, socket.AF_UNIX, socket.SOCK_STREAM)
        server_sock.setblocking(1)
        server_sock.send("OneButton default loopback profile:\n")

        try:
            while True:
                data = server_sock.recv(1024)
                server_sock.send("looping back: %s\n" % data)
        except IOError:
                pass

        server_sock.close()


    @dbus.service.method(PROFILE_INTERFACE, in_signature="o", out_signature="")
    def RequestDisconnection(self, path):
        if( self._fd > 0 ):
            close(self._fd)
            self._fd = -1
