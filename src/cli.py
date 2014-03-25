import Pyro4
from org.muscat.staldates.aldatesx.controller.Controller import *
from argparse import ArgumentParser

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("-c",
                        help="Specify the controller ID to connect to",
                        metavar="CONTROLLERID",
                        default="")
    args = parser.parse_args()

    if args.c != "":
        controllerAddress = "PYRONAME:" + Controller.pyroName + "." + args.c
    else:
        controllerAddress = "PYRONAME:" + Controller.pyroName

    logging.info("Connecting to controller at " + controllerAddress)

    c = Pyro4.Proxy(controllerAddress)
    remoteVersion = c.getVersion()

    if remoteVersion != Controller.version:
        raise VersionMismatchError(remoteVersion, Controller.version)
    print "Controller c available."
