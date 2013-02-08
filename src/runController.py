#!/usr/bin/python
from org.muscat.staldates.aldatesx.Controller import Controller
from org.muscat.staldates.aldatesx.devices.KramerVP88 import KramerVP88
import Pyro4
import subprocess
import atexit
import logging
from org.muscat.staldates.aldatesx.devices.VISCACamera import VISCACamera
from org.muscat.staldates.aldatesx.devices.KramerVP703 import KramerVP703

def shutdownDaemon(daemon):
    daemon.shutdown()

if __name__ == "__main__":
    controller = Controller()
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO)
    
    
    ##### Aldates configuration below
    
    mainSwitcher = KramerVP88("Main", "/dev/pts/7", 1)
    controller.addDevice(mainSwitcher)
    
    cam1 = VISCACamera("Camera 1", "/dev/pts/7", 1)
    controller.addDevice(cam1)
    
    scan1 = KramerVP703("Extras Scan Converter", "/dev/pts/7")
    controller.addDevice(scan1)
    
    #extrasSwitcher = Inline3808("Extras", "/dev/ttyUSB0")
    #controller.addDevice(extrasSwitcher)
    
    ##### Aldates configuration above
    
    controller.initialise()

    ip = subprocess.check_output( ["hostname", "-I"]  ).rstrip()
    logging.info("Using " + ip + " as hostname")
    Pyro4.config.HOST = ip 
    daemon = Pyro4.Daemon()
    ns = Pyro4.locateNS()
    uri = daemon.register(controller)
    ns.register(Controller.pyroName, uri)
    
    atexit.register(shutdownDaemon, daemon = daemon)
    
    daemon.requestLoop()
