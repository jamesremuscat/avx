#!/usr/bin/python
from org.muscat.staldates.aldatesx.Controller import Controller
from org.muscat.staldates.aldatesx.devices.KramerVP88 import KramerVP88,\
    KramerVP88Listener
from org.muscat.staldates.aldatesx.devices.Inline3808 import Inline3808
from org.muscat.staldates.aldatesx.devices.Kramer602 import Kramer602,\
    Kramer602Listener
from org.muscat.staldates.aldatesx.devices.VISCACamera import VISCACamera
from org.muscat.staldates.aldatesx.devices.KramerVP703 import KramerVP703
import Pyro4
import atexit
import logging
import json
from org.muscat.staldates.aldatesx.devices.SerialRelayCard import JBSerialRelayCard,\
    UpDownStopRelay, UpDownStopArray
from org.muscat.staldates.aldatesx import PyroUtils


def shutdownDaemon(daemon):
    daemon.shutdown()


def get_class(kls):
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    m = __import__(module)
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.DEBUG)
    controller = Controller()

    config = json.load(open("config.json"))

    for deviceID in config["devices"]:
        dc = config["devices"][deviceID]
        device = get_class(dc["class"])(deviceID, dc["port"], **dc["options"])
        print device

    ##### Aldates configuration below
#     mainSwitcher = KramerVP88("Main", "/dev/usb-ports/1-1.3.3:1.0", 1)
#     controller.addDevice(mainSwitcher)

#     mainListener = KramerVP88Listener(mainSwitcher, machineNumber=1)
#     mainListener.registerDispatcher(controller)
#     mainListener.start()
#     atexit.register(mainListener.stop)
#
#     prevSwitcher = Kramer602("Preview", "/dev/usb-ports/1-1.3.7:1.0")
#     controller.addDevice(prevSwitcher)
#
#     prevListener = Kramer602Listener(prevSwitcher, machineNumber=1)
#     prevListener.registerDispatcher(controller)
#     prevListener.start()
#     atexit.register(prevListener.stop)
#
#     cam1 = VISCACamera("Camera 1", "/dev/usb-ports/1-1.3.1.2", 1)
#     controller.addDevice(cam1)
#
#     cam2 = VISCACamera("Camera 2", "/dev/usb-ports/1-1.3.1.3", 1)
#     controller.addDevice(cam2)
#
#     cam3 = VISCACamera("Camera 3", "/dev/usb-ports/1-1.3.2:1.0", 1)
#     controller.addDevice(cam3)
#
#     scan1 = KramerVP703("Extras Scan Converter", "/dev/usb-ports/1-1.3.6:1.0")
#     controller.addDevice(scan1)
#
#     extrasSwitcher = Inline3808("Extras", "/dev/usb-ports/1-1.3.4:1.0")
#     controller.addDevice(extrasSwitcher)
#
#     powerSwitches = JBSerialRelayCard("Power", "/dev/usb-ports/1-1.2.1:1.0")
#     controller.addDevice(powerSwitches)
#
#     blindsOneToThree = JBSerialRelayCard("Blinds 1-4", "/dev/usb-ports/1-1.2.2:1.0")
#     blindsFourToSix = JBSerialRelayCard("Blinds 5-8", "/dev/usb-ports/1-1.2.3:1.0")
#
#     blind1 = UpDownStopRelay("Blind 1", blindsOneToThree.createDevice("blind1_updown", 2), blindsOneToThree.createDevice("blind1_gostop", 1))
#     blind2 = UpDownStopRelay("Blind 2", blindsOneToThree.createDevice("blind2_updown", 8), blindsOneToThree.createDevice("blind2_gostop", 7))
#     blind3 = UpDownStopRelay("Blind 3", blindsOneToThree.createDevice("blind3_updown", 6), blindsOneToThree.createDevice("blind3_gostop", 5))
#     blind4 = UpDownStopRelay("Blind 4", blindsFourToSix.createDevice("blind4_updown", 4), blindsFourToSix.createDevice("blind4_gostop", 3))
#     blind5 = UpDownStopRelay("Blind 5", blindsFourToSix.createDevice("blind5_updown", 2), blindsFourToSix.createDevice("blind5_gostop", 1))
#     blind6 = UpDownStopRelay("Blind 6", blindsFourToSix.createDevice("blind6_updown", 8), blindsFourToSix.createDevice("blind6_gostop", 7))
#
#     blinds = UpDownStopArray("Blinds", {1: blind1, 2: blind2, 3: blind3, 4: blind4, 5: blind5, 6: blind6})
#     controller.addDevice(blinds)
#
#     screen1 = UpDownStopRelay("Screen 1", powerSwitches.createDevice("screen1_updown", 4), powerSwitches.createDevice("screen1_gostop", 3))
#     screen2 = UpDownStopRelay("Screen 2", powerSwitches.createDevice("screen2_updown", 8), powerSwitches.createDevice("screen2_gostop", 7))
#     screens = UpDownStopArray("Screens", {1: screen1, 2: screen2})
#     controller.addDevice(screens)

    ##### Aldates configuration above

    controller.initialise()

    PyroUtils.setHostname()

    daemon = Pyro4.Daemon()
    ns = Pyro4.locateNS()
    uri = daemon.register(controller)
    ns.register(Controller.pyroName, uri)

    atexit.register(shutdownDaemon, daemon=daemon)

    daemon.requestLoop()
