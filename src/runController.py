#!/usr/bin/python
from argparse import ArgumentParser, FileType
from org.muscat.staldates.aldatesx.controller.Controller import Controller
import logging

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-d", "--debug",
                        help="Show debugging output.",
                        action="store_true")
    parser.add_argument("-c", "--config",
                        help="Configuration file to use",
                        default="config.json",
                        type=FileType("r"))
    args = parser.parse_args()
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=(logging.DEBUG if args.debug else logging.INFO))
    controller = Controller()
    controller.loadConfig(args.config)
    controller.initialise()
    controller.startServing()
