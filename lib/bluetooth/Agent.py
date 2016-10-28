import dbus.service

from . import BUS_NAME

AGENT_INTERFACE = '%s.Agent1' % BUS_NAME

class Agent(dbus.service.Object):
    bus = None

    def __init__(self, bus, object_path):
        dbus.service.Object.__init__(self, bus, object_path)
        self.bus = bus

    def set_trusted(path):
        props = self.dbus.Interface(self.bus.get_object(BUS_NAME, path), "org.freedesktop.DBus.Properties")
        props.Set("org.bluez.Device1", "Trusted", True)

    @dbus.service.method(AGENT_INTERFACE, in_signature="", out_signature="")
    def Release(self):
        print("Release")

    @dbus.service.method(AGENT_INTERFACE, in_signature="os", out_signature="")
    def AuthorizeService(self, device, uuid):
        print("AuthorizeService (%s, %s)" % (device, uuid))

    @dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="s")
    def RequestPinCode(self, device):
        """Disabled - implementation have only display"""
        print("RequestPinCode (%s) - no way to enter pin code" % (device))
        self.set_trusted(device)
        return

    @dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="u")
    def RequestPasskey(self, device):
        """Disabled - implementation have only display"""
        print("RequestPasskey (%s) - no way to enter pass code" % (device))
        self.set_trusted(device)
        return

    @dbus.service.method(AGENT_INTERFACE, in_signature="ouq", out_signature="")
    def DisplayPasskey(self, device, passkey, entered):
        print("DisplayPasskey (%s, %06u entered %u)" % (device, passkey, entered))

    @dbus.service.method(AGENT_INTERFACE, in_signature="os", out_signature="")
    def DisplayPinCode(self, device, pincode):
        print("DisplayPinCode (%s, %s)" % (device, pincode))

    @dbus.service.method(AGENT_INTERFACE, in_signature="ou", out_signature="")
    def RequestConfirmation(self, device, passkey):
        print("RequestConfirmation (%s, %06d)" % (device, passkey))
        return

    @dbus.service.method(AGENT_INTERFACE, in_signature="o", out_signature="")
    def RequestAuthorization(self, device):
        print("RequestAuthorization (%s)" % (device))
        return

    @dbus.service.method(AGENT_INTERFACE, in_signature="", out_signature="")
    def Cancel(self):
        print("Cancel")

