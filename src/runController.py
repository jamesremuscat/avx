#!/usr/bin/python
from org.muscat.staldates.aldatesx.Controller import Controller
from org.muscat.staldates.aldatesx.devices.KramerVP88 import KramerVP88
import Pyro4
import subprocess
#from org.muscat.staldates.aldatesx.devices.VISCACamera import VISCACamera


if __name__ == "__main__":
    controller = Controller()
    
    ##### Aldates configuration below
    
    mainSwitcher = KramerVP88("Main", "/dev/ttyUSB0", 1)
    controller.addDevice(mainSwitcher)
    
    #cam1 = VISCACamera("Camera 1", "/dev/ttyUSB0", 1)
    #controller.addDevice(cam1)
    
    #extrasSwitcher = Inline3808("Extras", "/dev/ttyUSB0")
    #controller.addDevice(extrasSwitcher)
    
    ##### Aldates configuration above

    ip = subprocess.check_output( ["hostname", "-I"]  ).rstrip()
    print "Using " + ip + " as hostname"
    Pyro4.config.HOST = ip 
    daemon = Pyro4.Daemon()
    ns = Pyro4.locateNS()
    uri = daemon.register(controller)
    ns.register(Controller.pyroName, uri)
    
    daemon.requestLoop()
