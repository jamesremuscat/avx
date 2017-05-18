'''
Created on 10 Nov 2012

@author: james
'''
from avx.devices.serial import SerialDevice
from avx.Client import MessageTypes

import logging


class KramerVP88(SerialDevice):
    '''
    A Kramer VP88 switcher, controlled by Protocol 2000 over serial.
    '''

    def __init__(self, deviceID, serialDevice, machineNumber=1, **kwargs):
        super(KramerVP88, self).__init__(deviceID, serialDevice, **kwargs)
        self.machineNumber = machineNumber

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

    def hasFullMessage(self, recv_buffer):
        return len(recv_buffer) == 4

    def handleMessage(self, msgBytes):
        logging.debug("Received from Kramer VP-88: " + SerialDevice.byteArrayToString(msgBytes).encode('hex_codec'))
        print msgBytes, 0x80 + self.machineNumber
        if (msgBytes[3] == 0x80 + self.machineNumber):
            if (msgBytes[0] == 0x41) or (msgBytes[0] == 0x45):  # Notification of video switch or response to query
                inp = msgBytes[1] - 0x80
                outp = msgBytes[2] - 0x80
                self.broadcast(MessageTypes.OUTPUT_MAPPING, {outp: inp})
