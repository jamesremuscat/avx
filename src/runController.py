#!/usr/bin/python
from org.muscat.staldates.aldatesx.Controller import Controller
import Pyro4
import atexit
import logging
import json
from org.muscat.staldates.aldatesx import PyroUtils
from org.muscat.staldates.aldatesx.devices.Device import Device


def shutdownDaemon(daemon):
    daemon.shutdown()


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.DEBUG)
    controller = Controller()

    try:
        config = json.load(open("config.json"))

        for d in config["devices"]:
            device = Device.create(d, controller)
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
