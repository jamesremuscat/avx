#!/usr/bin/python
from argparse import ArgumentParser
from org.muscat.staldates.aldatesx.controller.Controller import Controller
import logging

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-d", "--debug",
                        help="Show debugging output.",
                        action="store_true")
    args = parser.parse_args()
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=(logging.DEBUG if args.debug else logging.INFO))
    controller = Controller()
    controller.loadConfig("config.json")
    controller.initialise()
    controller.startServing()
