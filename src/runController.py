#!/usr/bin/python
from org.muscat.staldates.aldatesx.Controller import Controller
import Pyro4
import atexit
import logging
from org.muscat.staldates.aldatesx import PyroUtils


def shutdownDaemon(daemon):
    daemon.shutdown()


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.DEBUG)
    controller = Controller()
    controller.loadConfig("config.json")
    controller.initialise()

    PyroUtils.setHostname()

    daemon = Pyro4.Daemon()
    ns = Pyro4.locateNS()
    uri = daemon.register(controller)
    ns.register(Controller.pyroName, uri)

    atexit.register(shutdownDaemon, daemon=daemon)

    daemon.requestLoop()
