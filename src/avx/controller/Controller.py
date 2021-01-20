from argparse import ArgumentParser, FileType
from avx import PyroUtils, _version
from avx.controller.ControllerHttp import ControllerHttp
from avx.controller.messagebus import make_messagebus, MessageBus, PYRO_MSGBUS_NAME
from avx.devices import Device
from avx.Sequencer import Sequencer
from avx.utils import loadState, saveState
from logging import Handler
from Pyro4.errors import PyroError, NamingError
from semantic_version import Version as SemVer
import atexit
import logging.config
import Pyro4
import json

Pyro4.config.SERIALIZER = 'pickle'
Pyro4.config.SERIALIZERS_ACCEPTED.add('pickle')
Pyro4.config.REQUIRE_EXPOSE = False


def versionsCompatible(remote, local):
    rv = SemVer(remote)
    lv = SemVer(local)
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
        self.slaves = []
        self.daemon = Pyro4.Daemon(PyroUtils.getHostname())
        self.messagebus = None

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

        except ValueError:
            logging.exception("Cannot parse config.json!")

    def registerClient(self, clientURI):
        logging.warn('Client {} called deprecated and non-functional method registerClient'.format(clientURI))

    def unregisterClient(self, clientURI):
        logging.warn('Client {} called deprecated and non-functional method unegisterClient'.format(clientURI))

    def broadcast(self, msgType, source, data=None):
        ''' Send a message to all clients '''
        logging.debug("Broadcast: {}, {}, {}".format(msgType, source, data))
        if self.messagebus:
            self.messagebus.send_no_ack('avx', (msgType, source, data))
        for device in self.devices.values():
            if hasattr(device, 'receiveMessage'):
                device.receiveMessage(msgType, source, data)
        for slave in self.slaves:
            slave.broadcast(msgType, source, data)

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

        logging.info('Registering messagebus...')
        make_messagebus.storagetype = 'memory'
        messagebus_uri = self.daemon.register(MessageBus)
        ns.register(PYRO_MSGBUS_NAME, messagebus_uri)

        self.messagebus = Pyro4.Proxy('PYRONAME:' + PYRO_MSGBUS_NAME)

        atexit.register(lambda: self.daemon.shutdown())
        logging.info('Entering request loop')

        self.daemon.requestLoop()

    def sequence(self, *events):
        self.sequencer.sequence(*events)

    def getLog(self):
        return self.logHandler.entries


class DeviceProxy(object):
    def __init__(self, controller, deviceID):
        self._proxy = Pyro4.Proxy(controller.proxyDevice(deviceID))
        self._controller = controller
        self._deviceID = deviceID
        self._attr_cache = {}

    def proxy_attribute(self, attr, name):
        if not callable(attr):
            return attr
        else:
            def proxy(*args, **kwargs):
                try:
                    return attr(*args, **kwargs)
                except (Pyro4.errors.CommunicationError, Pyro4.errors.ConnectionClosedError):
                    # These tend to happen when the controller restarts, and all our device proxies get different URIs/ports
                    self._invalidate_cache()
                    self._reproxy()
                    return getattr(self, name)(*args, **kwargs)
            return proxy

    def _invalidate_cache(self):
        self._attr_cache.clear()

    def _reproxy(self):
        self._proxy = Pyro4.Proxy(self._controller.proxyDevice(self._deviceID))

    def __getattr__(self, name):
        if name not in self._attr_cache:
            self._attr_cache[name] = self.proxy_attribute(getattr(self._proxy, name), name)

        return self._attr_cache[name]


class ControllerProxy(object):
    def __init__(self, controller):
        self.controller = controller

    def __getattr__(self, name):
        return getattr(self.controller, name)

    def __getitem__(self, item):
        return DeviceProxy(self, item)


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
