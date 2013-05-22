from org.muscat.staldates.aldatesx.devices.Device import Device
from serial import Serial, SerialException
import logging
import threading
from threading import Thread


class SerialDevice(Device):
    '''
    A device we connect to over a serial port.
    '''

    def __init__(self, deviceID, serialDevice, baud=9600):
        '''
        Create a SerialDevice with a given device ID, using a new Serial with the given device address
        (e.g. "/dev/ttyUSB0") if given as a string, else assume serialDevice is a Serial and use that.
        If we fail to create a Serial with the given device, log an error and use a fake port.
        '''
        super(SerialDevice, self).__init__(deviceID)
        if isinstance(serialDevice, str):
            try:
                self.port = Serial(serialDevice, baud)
            except SerialException:
                logging.error("Could not open serial device " + serialDevice + " for " + deviceID)
                self.port = FakeSerialPort()
        else:
            self.port = serialDevice

    def sendCommand(self, commandString):
        logging.debug("Sending " + commandString.encode('hex_codec') + " to " + self.port.portstr)
        sentBytes = self.port.write(commandString)
        logging.debug(str(sentBytes) + " bytes sent")
        return sentBytes

    @staticmethod
    def byteArrayToString(byteArray):
        return ''.join(chr(b) for b in byteArray)


class SerialListener(Thread):
    ''' Class to listen to and interpret incoming messages from a serial device.
        Should implement a process(message) method where message is the hex array received.
    '''

    dispatchers = []

    def __init__(self, port):
        ''' port should be an already initialised Serial. '''
        Thread.__init__(self)
        self.port = port
        self.running = True

    def registerDispatcher(self, dispatcher):
        self.dispatchers.append(dispatcher)

    def stop(self):
        self.running = False

    def run(self):
        logging.info("Listening to serial port " + self.port.portstr)
        while self.running:
            message = [int(elem.encode("hex"), base=16) for elem in self.port.read(4)]
            self.process(message)
        logging.info("No longer listening to serial port " + self.port.portstr)


class FakeSerialPort(object):
    '''
    A class that quacks like a Serial if you try and write to it, but just throws everything away.
    '''
    portstr = "FAKE"

    def write(self, stuff):
        return 0

    def read(self, length):
        threading.Condition().wait()  # Block forever since we're never sending data here...
