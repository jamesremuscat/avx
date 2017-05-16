from avx.devices.Device import Device
from serial import Serial, SerialException
from threading import Thread

import atexit
import logging
import time


class SerialDevice(Device):
    '''
    A device we connect to over a serial port.
    '''

    def __init__(self, deviceID, serialDevice, baud=9600, **kwargs):
        '''
        Create a SerialDevice with a given device ID, using a new Serial with the given device address
        (e.g. "/dev/ttyUSB0") if given as a string, else assume serialDevice is a Serial and use that.
        If we fail to create a Serial with the given device, log an error and use a fake port.
        '''
        super(SerialDevice, self).__init__(deviceID, **kwargs)
        if isinstance(serialDevice, str) or isinstance(serialDevice, unicode):
            try:
                self.port = Serial(serialDevice, baud, timeout=2)
            except (SerialException, OSError):
                logging.exception("Could not open serial device " + serialDevice + " for " + deviceID)
                self.port = FakeSerialPort()
        else:
            self.port = serialDevice
        self.recv_thread = None
        self.dispatchers = []

    def initialise(self):
        self.recv_buffer = []
        self.run_receive = True
        if not (self.recv_thread and self.recv_thread.is_alive()):
            self.recv_thread = Thread(target=self._receive)
            self.recv_thread.daemon = True
            self.recv_thread.start()

    def _receive(self):
        while self.run_receive:
            read_byte = self.port.read(1)
            if read_byte:
                self.recv_buffer.append(ord(read_byte))
                if self.hasFullMessage(self.recv_buffer[:]):
                    logging.debug("Received from {}: {}".format(self.deviceID, SerialDevice.byteArrayToString(self.recv_buffer).encode('hex_codec')))
                    self.handleMessage(self.recv_buffer[:])
                    self.recv_buffer = []

    def hasFullMessage(self, recv_buffer):
        # Default implementation: always return True. This is almost certainly not useful to you so override this!
        # This a a safe default which, combined with handleMessage below, means that if you don't care about
        # receiving messages then you can just forget about overriding the two methods.
        return True

    def handleMessage(self, msgBytes):
        # Default implementation: just ignore messages.
        pass

    def registerDispatcher(self, dispatcher):
        self.dispatchers.append(dispatcher)

    def sendCommand(self, commandString):
        try:
            logging.debug("Sending " + commandString.encode('hex_codec') + " to " + self.port.portstr)
            sentBytes = self.port.write(commandString)
            logging.debug(str(sentBytes) + " bytes sent")
            return sentBytes
        except SerialException:
            #  Retry just the once - experience suggests that this might help
            logging.warn("Failed sending command to " + self.deviceID + " on " + self.port.portstr + ", retrying...")
            try:
                self.port.close()
                self.port.open()
                sentBytes = self.port.write(commandString)
                logging.debug(str(sentBytes) + " bytes sent")
                return sentBytes
            except SerialException:
                logging.exception("Really failed sending command to " + self.deviceID + " on " + self.port.portstr)

    def deinitialise(self):
        self.run_receive = False
        self.port.close()

    @staticmethod
    def byteArrayToString(byteArray):
        return ''.join(chr(b) for b in byteArray)


class SerialListener(Thread):
    ''' Class to listen to and interpret incoming messages from a serial device.
        Should implement a process(message) method where message is the hex array received.
    '''

    dispatchers = []
    running = False

    def __init__(self, deviceID, parentDevice, messageSize=4):
        ''' parentDevice should be an already initialised SerialDevice. '''
        Thread.__init__(self)
        self.parentDevice = parentDevice
        self.deviceID = deviceID
        self.messageSize = messageSize
        atexit.register(self.stop)

    def registerDispatcher(self, dispatcher):
        self.dispatchers.append(dispatcher)

    def start(self):
        if not self.running:
            self.running = True
            Thread.start(self)

    def stop(self):
        self.running = False

    def initialise(self):
        self.start()

    def deinitialise(self):
        self.stop()

    def run(self):
        logging.info("Listening to serial port " + self.parentDevice.port.portstr)
        while self.running:
            message = [int(elem.encode("hex"), base=16) for elem in self.parentDevice.port.read(self.messageSize)]
            if len(message) == self.messageSize:
                self.process(message)
            elif len(message) != 0:
                logging.warn("Malformed packet from " + self.deviceID + ": " + SerialDevice.byteArrayToString(message).encode('hex_codec'))
        logging.info("No longer listening to serial port " + self.parentDevice.port.portstr)


class FakeSerialPort(object):
    '''
    A class that quacks like a Serial if you try and write to it, but just throws everything away.
    '''
    portstr = "FAKE"

    def write(self, stuff):
        return 0

    def read(self, length):
        time.sleep(1)
        return []

    def flushInput(self):
        return 0

    def close(self):
        pass
