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
from org.muscat.staldates.aldatesx.devices.SerialRelayCard import JBSerialRelayCard
from org.muscat.staldates.aldatesx import PyroUtils


def shutdownDaemon(daemon):
    daemon.shutdown()


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.DEBUG)
    controller = Controller()

    ##### Aldates configuration below
    mainSwitcher = KramerVP88("Main", "/dev/usb-ports/1-1.3.3:1.0", 1)
    controller.addDevice(mainSwitcher)

    mainListener = KramerVP88Listener(mainSwitcher, machineNumber=1)
    mainListener.registerDispatcher(controller)
    mainListener.start()
    atexit.register(mainListener.stop)

    prevSwitcher = Kramer602("Preview", "/dev/usb-ports/1-1.3.7:1.0")
    controller.addDevice(prevSwitcher)

    prevListener = Kramer602Listener(prevSwitcher, machineNumber=1)
    prevListener.registerDispatcher(controller)
    prevListener.start()
    atexit.register(prevListener.stop)

    cam1 = VISCACamera("Camera 1", "/dev/usb-ports/1-1.3.1.2", 1)
    controller.addDevice(cam1)

    cam2 = VISCACamera("Camera 2", "/dev/usb-ports/1-1.3.1.3", 1)
    controller.addDevice(cam2)

    cam3 = VISCACamera("Camera 3", "/dev/usb-ports/1-1.3.2:1.0", 1)
    controller.addDevice(cam3)

    scan1 = KramerVP703("Extras Scan Converter", "/dev/usb-ports/1-1.3.6:1.0")
    controller.addDevice(scan1)

    extrasSwitcher = Inline3808("Extras", "/dev/usb-ports/1-1.3.4:1.0")
    controller.addDevice(extrasSwitcher)

    powerSwitches = JBSerialRelayCard("Power", "/dev/usb-ports/1-1.2.1:1.0")
    controller.addDevice(powerSwitches)

    ##### Aldates configuration above

    controller.initialise()

    PyroUtils.setHostname()

    daemon = Pyro4.Daemon()
    ns = Pyro4.locateNS()
    uri = daemon.register(controller)
    ns.register(Controller.pyroName, uri)

    atexit.register(shutdownDaemon, daemon=daemon)

    daemon.requestLoop()
