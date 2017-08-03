from argparse import ArgumentParser, FileType
from avx import PyroUtils, _version
from avx.controller.ControllerHttp import ControllerHttp
from avx.devices import Device
from avx.Sequencer import Sequencer
from logging import Handler
from Pyro4.errors import NamingError
from semantic_version import Version as SemVer
import atexit
import logging.config
import Pyro4
import json

Pyro4.config.SERIALIZER = 'pickle'
Pyro4.config.SERIALIZERS_ACCEPTED.add('pickle')
Pyro4.config.REQUIRE_EXPOSE = False


def versionsCompatible(remote, local):
    rv = SemVer(remote, partial=True)
    lv = SemVer(local, partial=True)
    if rv.major == 0:
        return rv.major == lv.major and rv.minor == lv.minor
    return rv.major == lv.major and rv.minor >= lv.minor


class Controller(object):
    '''
    A Controller is essentially a bucket of devices, each identified with a string deviceID.
    '''
    pyroName = "avx.controller"
    version = _version.__version__

    def __init__(self):
        self.devices = {}
        self.proxies = {}
        self.sequencer = Sequencer(self)
        self.sequencer.start()
        self.logHandler = ControllerLogHandler()
        logging.getLogger().addHandler(self.logHandler)
        self.clients = []
        self.slaves = []
        self.daemon = Pyro4.Daemon(PyroUtils.getHostname())

    @staticmethod
    def fromPyro(controllerID=""):
        controllerAddress = "PYRONAME:" + Controller.pyroName
        if controllerID != "":
            controllerAddress += "." + controllerID
        logging.info("Creating proxy to controller at " + controllerAddress)

        controller = ControllerProxy(Pyro4.Proxy(controllerAddress))
        remoteVersion = controller.getVersion()
        if not versionsCompatible(remoteVersion, Controller.version):
            raise VersionMismatchError(remoteVersion, Controller.version)
        return controller

    def loadConfig(self, configFile, overrideToDebug=False):
        try:
            if isinstance(configFile, file):
                config = json.load(configFile)
                self.configFile = configFile.name
            else:
                config = json.load(open(configFile))
                self.configFile = configFile

            self.config = config

            for d in config["devices"]:
                device = Device.create(d, self)
                self.addDevice(device)

            if "options" in config:

                if "controllerID" in config["options"]:
                    self.controllerID = config["options"]["controllerID"]

                if "slaves" in config["options"]:
                    for slave in config["options"]["slaves"]:
                        try:
                            sc = Controller.fromPyro(slave)

                            if versionsCompatible(sc.getVersion(), self.getVersion()):
                                self.slaves.append(sc)
                            else:
                                logging.error("This Controller is version " + str(self.getVersion()) + " but tried to add slave " + slave + " of version " + str(sc.getVersion()))
                        except NamingError:
                            logging.error("Could not connect to slave with controller ID " + slave)

                if "http" in config["options"]:
                    if config["options"]["http"] is True:
                        ch = ControllerHttp(self)
                        ch.start()

            if "logging" in config:
                logging.config.dictConfig(config["logging"])
                if overrideToDebug:
                    logging.getLogger().setLevel(logging.DEBUG)
                    logging.info("-d specified, overriding any specified default logger level to DEBUG")

            if "clients" in config:
                self.clients = list(config["clients"])
            self.config["clients"] = self.clients

        except ValueError:
            logging.exception("Cannot parse config.json!")

    def saveConfig(self):
        if hasattr(self, "configFile"):
            try:
                with open(self.configFile, "w") as cfout:
                    json.dump(self.config, cfout)
            except IOError:
                logging.exception("Cannot save config file!")

    def registerClient(self, clientURI):
        self.clients.append(str(clientURI))
        logging.info("Registered client at " + str(clientURI))
        logging.info(str(len(self.clients)) + " client(s) now connected")
        self.saveConfig()

    def unregisterClient(self, clientURI):
        self.clients.remove(str(clientURI))
        logging.info("Unregistered client at " + str(clientURI))
        logging.info(str(len(self.clients)) + " client(s) still connected")
        self.saveConfig()

    def broadcast(self, msgType, source, data=None):
        ''' Send a message to all clients '''
        logging.debug("Broadcast: {}, {}, {}".format(msgType, source, data))
        for uri in list(self.clients):
            try:
                logging.debug("Calling handleMessage on client at {}".format(uri))
                client = Pyro4.Proxy(uri)
                client._pyroTimeout = 1
                result = client.handleMessage(msgType, source, data)
                logging.debug("Client call returned " + str(result))
            except Exception:
                logging.exception("Failed to call handleMessage on registered client {}, removing.".format(uri))
                self.unregisterClient(uri)

    def getVersion(self):
        return self.version

    def addDevice(self, device):
        if self.hasDevice(device.deviceID):
            raise DuplicateDeviceIDError(device.deviceID)
        self.devices[device.deviceID] = device
        device.broadcast = lambda t, b=None: self.broadcast(t, device.deviceID, b)

    def getDevice(self, deviceID):
        return self.devices[deviceID]

    def proxyDevice(self, deviceID):
        if deviceID not in self.proxies.keys():
            if self.hasDevice(deviceID):
                self.proxies[deviceID] = self.daemon.register(self.getDevice(deviceID))
            else:
                for slave in self.slaves:
                    if slave.hasDevice(deviceID):
                        self.proxies[deviceID] = slave.proxyDevice(deviceID)
        return self.proxies[deviceID]

    def hasDevice(self, deviceID):
        return deviceID in self.devices

    def initialise(self):
        for device in self.devices.itervalues():
            device.initialise()
        atexit.register(self.deinitialise)

    def deinitialise(self):
        for device in self.devices.itervalues():
            device.deinitialise()

    def startServing(self):
        PyroUtils.setHostname()

        ns = Pyro4.locateNS()
        uri = self.daemon.register(self)

        if hasattr(self, "controllerID"):
            name = self.pyroName + "." + self.controllerID
        else:
            name = self.pyroName

        logging.info("Registering controller as " + name)

        ns.register(name, uri)

        atexit.register(lambda: self.daemon.shutdown())

        self.daemon.requestLoop()

    def sequence(self, *events):
        self.sequencer.sequence(*events)

    def getLog(self):
        return self.logHandler.entries


class ControllerProxy(object):
    def __init__(self, controller):
        self.controller = controller

    def __getattr__(self, name):
        return getattr(self.controller, name)

    def __getitem__(self, item):
        return Pyro4.Proxy(self.controller.proxyDevice(item))


class ControllerLogHandler(Handler):

    def __init__(self):
        Handler.__init__(self)
        self.entries = []

    def emit(self, record):
        self.entries.append(record)
        if len(self.entries) > 100:
            self.entries.pop(0)
        if record.exc_info is not None:
            record.exc_info = None
            fakeRecord = logging.LogRecord("Controller", logging.WARNING, record.pathname, record.lineno, "", {}, None, None)
            fakeRecord.created = record.created
            fakeRecord.asctime = record.asctime if hasattr(record, "asctime") else "--"
            self.format(fakeRecord)
            fakeRecord.message = "An exception was stripped from this log, see controller logs for details"
            self.entries.append(fakeRecord)


class VersionMismatchError(Exception):

    def __init__(self, remoteVersion, localVersion):
        super(VersionMismatchError, self).__init__("Controller is version " + str(remoteVersion) + " but this client is written for version " + str(localVersion) + ". Check your installation and try again.")


class DuplicateDeviceIDError(Exception):

    def __init__(self, duplicatedID):
        super(DuplicateDeviceIDError, self).__init__("Device already exists: " + duplicatedID)


def main():
    parser = ArgumentParser()
    parser.add_argument("-d", "--debug",
                        help="Show debugging output.",
                        action="store_true")
    parser.add_argument("-c", "--config",
                        help="Configuration file to use",
                        type=FileType("r"))
    args = parser.parse_args()
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=(logging.DEBUG if args.debug else logging.INFO))

    controller = Controller()
    logging.info("Starting avx controller v{}".format(controller.getVersion()))

    if args.config:
        controller.loadConfig(args.config, args.debug)
    else:
        try:
            configFile = open('config.json', 'r')
            controller.loadConfig(configFile)
        except IOError:
            logging.error("No config file specified and config.json not found! Exiting...")
            exit(1)
    controller.initialise()
    controller.startServing()
    logging.info("avx controller terminated.")


if __name__ == "__main__":
    main()
