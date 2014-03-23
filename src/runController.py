#!/usr/bin/python
from org.muscat.staldates.aldatesx.controller.Controller import Controller
import logging

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO)
    controller = Controller()
    controller.loadConfig("config.json")
    controller.initialise()
    controller.startServing()
