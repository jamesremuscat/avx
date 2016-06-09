'''
Created on 10 Nov 2012

@author: james
'''
from avx.devices.SerialDevice import SerialDevice, SerialListener
import logging
import Pyro4


class KramerVP88(SerialDevice):
    '''
    A Kramer VP88 switcher, controlled by Protocol 2000 over serial.
    '''

    def __init__(self, deviceID, serialDevice, machineNumber=1, **kwargs):
        super(KramerVP88, self).__init__(deviceID, serialDevice, **kwargs)
        self.machineNumber = machineNumber

    @Pyro4.callback
    def sendInputToOutput(self, inChannel, outChannel):
        toSend = [0x01, 0x80 + int(inChannel), 0x80 + int(outChannel), 0x80 + self.machineNumber]
        return self.sendCommand(SerialDevice.byteArrayToString(toSend))

    def initialise(self):
        SerialDevice.initialise(self)
        self.port.flushInput()
        self.requestStatus()

    def requestStatus(self):
        for i in range(1, 9):
            self.sendCommand(SerialDevice.byteArrayToString([0x05, 0x80, 0x80 + i, 0x80 + self.machineNumber]))


class KramerVP88Listener(SerialListener):
    ''' Class to listen to and interpret incoming messages from a VP88. '''

    dispatchers = []

    def __init__(self, deviceID, parent, controller, machineNumber=1):
        ''' Initialise this KramerVP88 listener. parent should be the name of a KramerVP88 device within the controller. '''
        super(KramerVP88Listener, self).__init__(deviceID, controller.getDevice(parent))
        self.machineNumber = machineNumber

    def process(self, message):
        logging.debug("Received from Kramer VP-88: " + SerialDevice.byteArrayToString(message).encode('hex_codec'))
        if (message[3] == 0x80 + self.machineNumber):
            if (message[0] == 0x41) or (message[0] == 0x45):  # Notification of video switch or response to query
                inp = message[1] - 0x80
                outp = message[2] - 0x80
                for d in self.dispatchers:
                    d.updateOutputMappings({self.parentDevice.deviceID: {outp: inp}})
