#!/usr/bin/python
from org.muscat.staldates.aldatesx.Controller import Controller
import Pyro4
import atexit
import logging
import json
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

    try:
        config = json.load(open("config.json"))

        for device in config["devices"]:
            deviceID = device["deviceID"]
            logging.info("Creating device " + deviceID)
            device = get_class(device["class"])(deviceID, controller=controller, **device["options"])
            controller.addDevice(device)

        controller.initialise()

        PyroUtils.setHostname()

        daemon = Pyro4.Daemon()
        ns = Pyro4.locateNS()
        uri = daemon.register(controller)
        ns.register(Controller.pyroName, uri)

        atexit.register(shutdownDaemon, daemon=daemon)

        daemon.requestLoop()

    except ValueError:
        logging.exception("Cannot parse config.json:")
