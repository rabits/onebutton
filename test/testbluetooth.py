import dbus
try:
  from gi.repository import GObject
except ImportError:
  import gobject as GObject

import sys, os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from lib.bluetooth import (Agent, Profile, BUS_NAME)

if __name__ == '__main__':
    mainloop = GObject.MainLoop()

    import dbus.mainloop.glib
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    bus = dbus.SystemBus()

    agent = Agent(bus, "/onebutton/agent")
    manager = dbus.Interface(bus.get_object(BUS_NAME, "/org/bluez"), "org.bluez.AgentManager1")
    manager.RegisterAgent("/onebutton/agent", "NoInputNoOutput")
    manager.RequestDefaultAgent("/onebutton/agent")

    print "Agent added"

    manager = dbus.Interface(bus.get_object(BUS_NAME, "/org/bluez"), "org.bluez.ProfileManager1")
    profile = Profile(bus, "/onebutton/service/control")
    profile_web = Profile(bus, "/onebutton/service/guitarix_web")

    opts = {
        "AutoConnect": True,
        "Name": "OneButton",
        "Role": "server",
        "PSM": dbus.UInt16(3),
        "Service": 'e48ccf70-59be-5383-afc6-3f5793a953ba',
        "Channel": dbus.UInt16(13),
        "RequireAuthentication": False,
        "RequireAuthorization": False
    }
#        "Service": "00001101-0000-1000-8000-00805f9b34fb"

    manager.RegisterProfile("/onebutton/service/control", '1101', opts)
#    manager.RegisterProfile("/onebutton/service/control", 'e48ccf70-59be-5383-afc6-3f5793a953ba', opts)

    opts = {
        "AutoConnect": True,
        "Name": "Guitarix WEB",
        "Role": "server",
        "PSM": dbus.UInt16(3),
        "Service": '8e6420b8-23f9-5c57-81d9-974deae472f1',
        "Channel": dbus.UInt16(12),
        "RequireAuthentication": False,
        "RequireAuthorization": False
    }

    manager.RegisterProfile("/onebutton/service/guitarix_web", '1101', opts)
#    manager.RegisterProfile("/onebutton/service/guitarix_web", '8e6420b8-23f9-5c57-81d9-974deae472f1', opts)

    print "Profiles added"

#    objects = dbus.Interface(bus.get_object(BUS_NAME, "/"),"org.freedesktop.DBus.ObjectManager").GetManagedObjects()

#    adapters = []
#    for path, ifaces in objects.iteritems():
#        adapter = ifaces.get("org.bluez.Adapter1")
#        if adapter is None:
#            continue
#        adapters.append(dbus.Interface(bus.get_object(BUS_NAME, path), "org.bluez.Adapter1"))
#        print("%s %s" % (ifaces["org.bluez.Adapter1"]["Address"], ifaces["org.bluez.Adapter1"]["Alias"]))
#        print("  Powered: %s" % ifaces["org.bluez.Adapter1"]["Powered"])
#        print("  Discoverable: %s" % ifaces["org.bluez.Adapter1"]["Discoverable"])
#        print("  Pairable: %s" % ifaces["org.bluez.Adapter1"]["Pairable"])
#        print("  UUIDs: %s" % ifaces["org.bluez.Adapter1"]["UUIDs"])

#    for d in adapters:
#        print("path: %s" % d.object_path)

    #devices[0].Connect()
#    print("Profiles connected")

    mainloop.run()
