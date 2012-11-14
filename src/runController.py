#!/usr/bin/python
from org.muscat.staldates.aldatesx.Controller import Controller
from org.muscat.staldates.aldatesx.devices.KramerVP88 import KramerVP88
import Pyro4


if __name__ == "__main__":
    controller = Controller()
    
    ##### Aldates configuration below
    
    mainSwitcher = KramerVP88("Main", "/dev/ttyUSB0", 1)
    controller.addDevice(mainSwitcher)
    
    #extrasSwitcher = Inline3808("Extras", "/dev/ttyUSB0")
    #controller.addDevice(extrasSwitcher)
    
    ##### Aldates configuration above
    
    daemon = Pyro4.Daemon()
    ns = Pyro4.locateNS()
    uri = daemon.register(controller)
    ns.register("aldates.alix", uri)
    
    daemon.requestLoop()