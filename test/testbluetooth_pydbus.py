from __future__ import print_function

from gi.repository import GLib
from lib.pydbus import SystemBus

import socket
import bluetooth as bt

import sys, os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


###
## For some reason on new connection return fd = 0
###

class Agent(object):
    '''
    <node>
        <interface name='org.bluez.Agent1'>
            <method name='Release'></method>
            <method name='AuthorizeService'>
                <arg type='o' name='device' direction='in'/>
                <arg type='s' name='uuid' direction='in'/>
            </method>
            <method name='RequestPinCode'>
                <arg type='o' name='device' direction='in'/>
                <arg type='s' name='pin_code' direction='out'/>
            </method>
            <method name='RequestPasskey'>
                <arg type='o' name='device' direction='in'/>
                <arg type='u' name='pass_key' direction='out'/>
            </method>
            <method name='DisplayPasskey'>
                <arg type='o' name='device' direction='in'/>
                <arg type='u' name='pass_key' direction='in'/>
                <arg type='q' name='entered' direction='in'/>
            </method>
            <method name='DisplayPinCode'>
                <arg type='o' name='device' direction='in'/>
                <arg type='s' name='pin_code' direction='in'/>
            </method>
            <method name='RequestConfirmation'>
                <arg type='o' name='device' direction='in'/>
                <arg type='s' name='pass_key' direction='in'/>
            </method>
            <method name='RequestAuthorization'>
                <arg type='o' name='device' direction='in'/>
            </method>
        <method name='Cancel'></method>
        </interface>
    </node>
    '''

    bus = None

    def __init__(self, bus, object_path):
        self.bus = bus
        bus.publish(object_path[1:].replace('/', '.'), self)

    def set_trusted(path):
        props = self.bus.get('org.bluez', path)['org.freedesktop.DBus.Properties']
        print('trust', path)
        props.Set("org.bluez.Device1", "Trusted", GLib.Variant.new_boolean(True))

    def Release(self):
        print("Release")

    def AuthorizeService(self, device, uuid):
        print("AuthorizeService (%s, %s)" % (device, uuid))

    def RequestPinCode(self, device):
        """Disabled - implementation has only display"""
        print("RequestPinCode (%s) - no way to enter pin code" % (device))
        self.set_trusted(device)
        return

    def RequestPasskey(self, device):
        """Disabled - implementation has only display"""
        print("RequestPasskey (%s) - no way to enter pass code" % (device))
        self.set_trusted(device)
        return

    def DisplayPasskey(self, device, passkey, entered):
        print("DisplayPasskey (%s, %06u entered %u)" % (device, passkey, entered))

    def DisplayPinCode(self, device, pincode):
        print("DisplayPinCode (%s, %s)" % (device, pincode))

    def RequestConfirmation(self, device, passkey):
        print("RequestConfirmation (%s, %06d)" % (device, passkey))
        return

    def RequestAuthorization(self, device):
        print("RequestAuthorization (%s)" % (device))
        return

    def Cancel(self):
        print("Cancel")

class Profile(object):
    '''
    <node>
        <interface name='org.bluez.Profile1'>
            <method name='Release'></method>
            <method name='RequestDisconnection'>
                <arg type='o' name='device' direction='in'/>
            </method>
            <method name='NewConnection'>
                <arg type='o' name='device' direction='in'/>
                <arg type='h' name='fd' direction='in'/>
                <arg type='a{sv}' name='fd_properties' direction='in'/>
            </method>
        </interface>
    </node>
    '''
    conns = {}
    _sock = -1

    def __init__(self, bus, object_path):
        bus.publish(object_path[1:].replace('/', '.'), self)

    def Release(self):
        print("Release")

    def RequestDisconnection(self, device):
        print('RequestDisconnection from %s' % device)
        #conns.pop(device).close()

    def NewConnection(self, device, fd, fd_properties):
        print("New connectin from %s %s" % (device, fd))
        print(dir(fd))
        print(type(fd))
        if fd <= 0:
            print("FD is invalid %s" % fd)
            return

        self.conns[device] = fd

        print("taken")
        for key in fd_properties.keys():
            if key == "Version" or key == "Features":
                print("  %s = 0x%04x" % (key, fd_properties[key]))
            else:
                print("  %s = %s" % (key, fd_properties[key]))

        print("test1")
        server_sock = socket.fromfd(self.conns[device], socket.AF_UNIX, socket.SOCK_STREAM)
        print("test2")
        server_sock.setblocking(1)
        print("test3")
        server_sock.send("OneButton default loopback profile:\n")

        try:
            print("test4")
            while True:
                data = server_sock.recv(1024)
                print("received: %s" % data)
                server_sock.send("looping back: %s\n" % data)
        except IOError:
                pass

        server_sock.close()


#
#        def new_intr_conn(ssock, ip_type):
#            sock, info = ssock.accept()
#            print("interrput connection:", info)
#            self.conns[device].register_intr_sock(sock)
#            return False
#
#        GLib.io_add_watch(self.sock, GLib.IO_IN, new_intr_conn)
# https://github.com/lvht/btk/blob/master/btk.py

if __name__ == '__main__':
    mainloop = GLib.MainLoop()

    bus = SystemBus()
    bus.own_name('org.rabits.onebutton')

    # open_hci()
    props = bus.get('org.bluez', '/org/bluez/hci0')['org.freedesktop.DBus.Properties']
    props.Set("org.bluez.Adapter1", "Powered", GLib.Variant.new_boolean(True))
    props.Set("org.bluez.Adapter1", "Discoverable", GLib.Variant.new_boolean(True))

    # register_agent()
    capability = "NoInputNoOutput"
    path = "/onebutton/agent"
    agent = Agent(bus, path)
    manager = bus.get('org.bluez')['.AgentManager1']
    manager.RegisterAgent(path, capability)
    manager.RequestDefaultAgent(path)

#    sock = bt.BluetoothSocket(bt.L2CAP)
#    sock.setblocking(False)
#    try:
#        sock.bind(('', 0x13))
#    except:
#        print("For bluez5 add --noplugin=input to the bluetoothd commandline")
#        print("Else there is another application running that has it open.")
#        sys.exit(errno.EACCES)
#    sock.listen(1)

    # register_profile()
    path = "/onebutton/service/guitarix_web"
    profile = Profile(bus, path)
    opts = {
        "AutoConnect": GLib.Variant.new_boolean(True),
        "Name": GLib.Variant.new_string("Guitarix WEB"),
        "Role": GLib.Variant.new_string("server"),
        "PSM": GLib.Variant.new_uint16(3),
        "Service": GLib.Variant.new_string('8e6420b8-23f9-5c57-81d9-974deae472f1'),
        "Channel": GLib.Variant.new_uint16(12),
        "RequireAuthentication": GLib.Variant.new_boolean(False),
        "RequireAuthorization": GLib.Variant.new_boolean(False)
    }
#    opts = {
#        "PSM": GLib.Variant.new_uint16(3),
#        "ServiceRecord": GLib.Variant.new_string('''
#            <?xml version="1.0" encoding="UTF-8" ?>
#            <record>
#                <attribute id="0x0001"><!-- ServiceClassIDList -->
#                    <sequence>
#                        <uuid value="8e6420b8-23f9-5c57-81d9-974deae472f1" />
#                        <uuid value="0x1101" />
#                    </sequence>
#                </attribute>
#                <attribute id="0x0003"><!-- ServiceID -->
#                    <uuid value="8e6420b8-23f9-5c57-81d9-974deae472f1" />
#                </attribute>
#                <attribute id="0x0004"><!-- ProtocolDescriptorList -->
#                    <sequence>
#                        <sequence>
#                            <uuid value="0x0100" />
#                        </sequence>
#                        <sequence>
#                            <uuid value="0x0003" />
#                            <uint8 value="0x01" />
#                        </sequence>
#                    </sequence>
#                </attribute>
#                <attribute id="0x0005"><!-- BrowseGroupList -->
#                    <sequence>
#                        <uuid value="0x1002" />
#                    </sequence>
#                </attribute>
#                <attribute id="0x0009"><!-- BluetoothProfileDescriptorList -->
#                    <sequence>
#                        <sequence>
#                            <uuid value="0x1101" />
#                            <uint16 value="0x0100" />
#                        </sequence>
#                    </sequence>
#                </attribute>
#                <attribute id="0x0100"><!-- Neutral Name -->
#                    <text value="Guitarix WEB" />
#                </attribute>
#            </record>'''),
#        "RequireAuthentication": GLib.Variant.new_boolean(False),
#        "RequireAuthorization": GLib.Variant.new_boolean(False)
#    }
    manager = bus.get('org.bluez')['.ProfileManager1']
    manager.RegisterProfile(path, '1101', opts)

    mainloop.run()

