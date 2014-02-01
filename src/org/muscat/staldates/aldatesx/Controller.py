from org.muscat.staldates.aldatesx.controller.VISCAController import VISCAController
from org.muscat.staldates.aldatesx.devices.Device import Device
from org.muscat.staldates.aldatesx.Sequencer import Sequencer, Event
import logging
from logging import Handler
import Pyro4
import json


class Controller(VISCAController):
    '''
    A Controller is essentially a bucket of devices, each identified with a string deviceID.
    '''
    pyroName = "aldates.alix.controller"
    version = 0.9

    def __init__(self):
        self.devices = {}
        self.sequencer = Sequencer()
        self.sequencer.start()
        self.logHandler = ControllerLogHandler()
        logging.getLogger().addHandler(self.logHandler)
        self.clients = []

    def loadConfig(self, configFile):
        try:
            config = json.load(open(configFile))
            for d in config["devices"]:
                device = Device.create(d, self)
                self.addDevice(device)
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

    def switch(self, deviceID, inChannel, outChannel):
        '''If a device with the given ID exists, perform a video switch. If not then return -1.'''
        if self.hasDevice(deviceID):
            logging.debug("Switching device " + deviceID + ": " + str(inChannel) + "=>" + str(outChannel))
            return self.devices[deviceID].sendInputToOutput(inChannel, outChannel)
        else:
            logging.warn("No device with ID " + deviceID)
            return -1

    def toggleOverscan(self, scDevice, overscan):
        if self.hasDevice(scDevice):
            sc = self.devices[scDevice]
            if overscan:
                sc.overscanOn()
            else:
                sc.overscanOff()
        else:
            logging.warn("No device with ID " + scDevice)
        return -1

    def toggleFreeze(self, scDevice, freeze):
        if self.hasDevice(scDevice):
            sc = self.devices[scDevice]
            if freeze:
                sc.freeze()
            else:
                sc.unfreeze()
        else:
            logging.warn("No device with ID " + scDevice)
        return -1

    def toggleOverlay(self, scDevice, overlay):
        if self.hasDevice(scDevice):
            sc = self.devices[scDevice]
            if overlay:
                sc.overlayOn()
            else:
                sc.overlayOff()
        else:
            logging.warn("No device with ID " + scDevice)
        return -1

    def toggleFade(self, scDevice, fade):
        if self.hasDevice(scDevice):
            sc = self.devices[scDevice]
            if fade:
                sc.fadeOut()
            else:
                sc.fadeIn()
        else:
            logging.warn("No device with ID " + scDevice)
        return -1

    def recalibrate(self, scDevice):
        if self.hasDevice(scDevice):
            sc = self.devices[scDevice]
            sc.recalibrate()
        else:
            logging.warn("No device with ID " + scDevice)
        return -1

    def raiseUp(self, device, number):
        if self.hasDevice(device):
            logging.debug("Raising " + device + ":" + str(number))
            d = self.devices[device]
            d.raiseUp(number)
        else:
            logging.warn("No device with ID " + device)
        return -1

    def lower(self, device, number):
        if self.hasDevice(device):
            logging.debug("Lowering " + device + ":" + str(number))
            d = self.devices[device]
            d.lower(number)
        else:
            logging.warn("No device with ID " + device)
        return -1

    def stop(self, device, number):
        if self.hasDevice(device):
            logging.debug("Stopping " + device + ":" + str(number))
            d = self.devices[device]
            d.stop(number)
        else:
            logging.warn("No device with ID " + device)
        return -1

    def systemPowerOn(self):
        if self.hasDevice("Power"):
            power = self.devices["Power"]
            logging.info("Turning ON system power")
            self.sequencer.sequence(
                Event(lambda: self.callAllClients(lambda c: c.showPowerOnDialog())),
                Event(power.on, 2),
                self.sequencer.wait(3),
                Event(power.on, 5),
                self.sequencer.wait(3),
                Event(power.on, 6),
                self.sequencer.wait(3),
                Event(power.on, 1),
                Event(self.initialise),  # By this time all things we care about to initialise will have been switched on
                Event(lambda: self.callAllClients(lambda c: c.hidePowerDialog())),
            )

    def systemPowerOff(self):
        if self.hasDevice("Power"):
            power = self.devices["Power"]
            logging.info("Turning OFF system power")
            self.sequencer.sequence(
                Event(lambda: self.callAllClients(lambda c: c.showPowerOffDialog())),
                Event(power.off, 1),
                self.sequencer.wait(3),
                Event(power.off, 6),
                self.sequencer.wait(3),
                Event(power.off, 5),
                self.sequencer.wait(3),
                Event(power.off, 2),
                Event(lambda: self.callAllClients(lambda c: c.hidePowerDialog())),
            )

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
