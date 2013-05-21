'''
Created on 10 Nov 2012

@author: james
'''
from org.muscat.staldates.aldatesx.devices.SerialDevice import SerialDevice
from threading import Thread
import logging


class KramerVP88(SerialDevice):
    '''
    A Kramer VP88 switcher, controlled by Protocol 2000 over serial.
    '''

    def __init__(self, deviceID, serialDevice, machineNumber=1):
        super(KramerVP88, self).__init__(deviceID, serialDevice)
        self.machineNumber = machineNumber

    def sendInputToOutput(self, inChannel, outChannel):
        toSend = [0x01, 0x80 + inChannel, 0x80 + outChannel, 0x80 + self.machineNumber]
        return self.sendCommand(SerialDevice.byteArrayToString(toSend))


class KramerVP88Listener(Thread):
    ''' Class to listen to and interpret incoming messages from a VP88. '''

    dispatchers = []

    def __init__(self, port, machineNumber=1):
        ''' Initialise this KramerVP88 listener. port should be the same Serial that's already been passed to a KramerVP88. '''
        Thread.__init__(self)
        self.port = port
        self.machineNumber = machineNumber
        self.running = True

    def registerDispatcher(self, dispatcher):
        self.dispatchers.append(dispatcher)

    def stop(self):
        self.running = False

    def run(self):
        logging.info("Listening for responses from Kramer VP-88 at " + self.port.portstr)
        while self.running:
            message = [int(elem.encode("hex"), base=16) for elem in self.port.read(4)]
            self.process(message)
        logging.info("No longer listening to Kramer VP-88 at " + self.port.portstr)

    def process(self, message):
        if (message[3] == 0x80 + self.machineNumber):
            if (message[0] == 0x41) or (message[0] == 0x45):  # Notification of video switch or response to query
                inp = message[1] - 0x80
                outp = message[2] - 0x80
                for d in self.dispatchers:
                    d.updateOutputMappings({outp: inp})
