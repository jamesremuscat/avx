from org.muscat.avx.controller.amBxController import amBxController
from org.muscat.avx.controller.ControllerHttp import ControllerHttp
from org.muscat.avx.controller.RelayController import RelayController
from org.muscat.avx.controller.ScanConverterController import ScanConverterController
from org.muscat.avx.controller.UnisonController import UnisonController
from org.muscat.avx.controller.UpDownRelayController import UpDownRelayController
from org.muscat.avx.controller.VideoSwitcherController import VideoSwitcherController
from org.muscat.avx.controller.VISCAController import VISCAController
from org.muscat.avx.devices.Device import Device
from org.muscat.avx.Sequencer import Sequencer
from org.muscat.avx import PyroUtils
import atexit
import logging
from logging import Handler
import Pyro4
import json
from Pyro4.errors import NamingError


class Controller(amBxController, RelayController, ScanConverterController, UnisonController, UpDownRelayController, VideoSwitcherController, VISCAController):
    '''
    A Controller is essentially a bucket of devices, each identified with a string deviceID.
    '''
    pyroName = "org.muscat.avx.controller"
    version = 0.10

    slaves = []

    def __init__(self):
        self.devices = {}
        self.sequencer = Sequencer(self)
        self.sequencer.start()
        self.logHandler = ControllerLogHandler()
        logging.getLogger().addHandler(self.logHandler)
        self.clients = []

    @staticmethod
    def fromPyro(controllerID=""):
        controllerAddress = "PYRONAME:" + Controller.pyroName
        if controllerID != "":
            controllerAddress += "." + controllerID
        logging.info("Creating proxy to controller at " + controllerAddress)

        return Pyro4.Proxy(controllerAddress)

    def loadConfig(self, configFile):
        try:
            if isinstance(configFile, file):
                config = json.load(configFile)
            else:
                config = json.load(open(configFile))
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

                            if sc.getVersion() == self.getVersion():
                                self.slaves.append(sc)
                            else:
                                logging.error("This Controller is version " + str(self.getVersion()) + " but tried to add slave " + slave + " of version " + str(sc.getVersion()))
                        except NamingError:
                            logging.error("Could not connect to slave with controller ID " + slave)

                if "http" in config["options"]:
                    if config["options"]["http"] == True:
                        ch = ControllerHttp(self)
                        ch.start()

        except ValueError:
            logging.exception("Cannot parse config.json:")

    def registerClient(self, clientURI):
        self.clients.append(clientURI)
        logging.info("Registered client at " + str(clientURI))
        logging.info(str(len(self.clients)) + " client(s) now connected")

    def unregisterClient(self, clientURI):
        self.clients.remove(clientURI)
        logging.info("Unregistered client at " + str(clientURI))
        logging.info(str(len(self.clients)) + " client(s) still connected")

    def callAllClients(self, function):
        ''' function should take a client and do things to it'''
        for uri in self.clients:
            try:
                logging.debug("Calling function " + function.__name__ + " with client at " + str(uri))
                client = Pyro4.Proxy(uri)
                result = function(client)
                logging.debug("Client call returned " + str(result))
            except:
                logging.exception("Failed to call function on registered client " + str(uri) + ", removing.")
                self.clients.pop(uri)

    def getVersion(self):
        return self.version

    def addDevice(self, device):
        if self.hasDevice(device.deviceID):
            raise DuplicateDeviceIDError(device.deviceID)
        self.devices[device.deviceID] = device
        if hasattr(device, "registerDispatcher") and callable(getattr(device, "registerDispatcher")):
            device.registerDispatcher(self)

    def getDevice(self, deviceID):
        return self.devices[deviceID]

    def hasDevice(self, deviceID):
        return deviceID in self.devices

    def initialise(self):
        for device in self.devices.itervalues():
            device.initialise()

    def startServing(self):
        PyroUtils.setHostname()

        daemon = Pyro4.Daemon()
        ns = Pyro4.locateNS()
        uri = daemon.register(self)

        if hasattr(self, "controllerID"):
            name = self.pyroName + "." + self.controllerID
        else:
            name = self.pyroName
        ns.register(name, uri)

        atexit.register(lambda: daemon.shutdown())

        daemon.requestLoop()

    def sequence(self, *events):
        self.sequencer.sequence(*events)

    def showPowerOnDialogOnClients(self):
        self.callAllClients(lambda c: c.showPowerOnDialog())

    def showPowerOffDialogOnClients(self):
        self.callAllClients(lambda c: c.showPowerOffDialog())

    def hidePowerDialogOnClients(self):
        self.callAllClients(lambda c: c.hidePowerDialog())

    def getLog(self):
        return self.logHandler.entries

    def updateOutputMappings(self, mapping):
        self.callAllClients(lambda c: c.updateOutputMappings(mapping))


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
