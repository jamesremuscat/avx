'''
Created on 13 Nov 2012

@author: jrem
'''
from avx.devices.serial import SerialDevice
from avx.Client import MessageTypes

import logging


class Kramer602(SerialDevice):
    '''
    The Kramer 602 (preview) switcher. Reverse-engineered from the AMX code, this is apparently not Protocol 2000...
    '''

    def __init__(self, deviceID, serialDevice, machineNumber=1, **kwargs):
        super(Kramer602, self).__init__(deviceID, serialDevice, 1200, **kwargs)
        self.machineNumber = machineNumber

    def sendInputToOutput(self, inChannel, outChannel):
        if outChannel > 2:
            logging.error("Output channel " + str(outChannel) + " does not exist on switcher " + self.deviceID)
        else:
            code = [0, 0x80 + (2 * inChannel) - (2 - outChannel)]
            self.sendCommand(SerialDevice.byteArrayToString(code))

    def initialise(self):
        SerialDevice.initialise(self)
        self.port.flushInput()
        self.requestStatus()

    '''Request the status of this switcher's outputs.'''
    def requestStatus(self):
        self.port.write("\x00\xA1")

    def hasFullMessage(self, recv_buffer):
        return (len(recv_buffer) == 2 and recv_buffer[1] != 0xFF) or len(recv_buffer) == 3

    def handleMessage(self, msgBytes):
        if len(msgBytes) == 3:
            msgBytes.pop(1)  # Get rid of the mysterious middle byte
        if ((msgBytes[0] & 0x7) == (self.machineNumber - 1)):
            if (msgBytes[1] & 0x20) == 0:  # Not just a "I switched successfully" message
                outp = (((msgBytes[1] & 0x1F) - 1) % 2) + 1
                inp = (((msgBytes[1] & 0x1F) - outp) / 2) + 1  # int(math.ceil((message[1] & 0x1F) + (2 / 2)) - 1)
                self.broadcast(MessageTypes.OUTPUT_MAPPING, {outp: inp})
            else:
                self.requestStatus()  # Request device to send current status so listener can intercept
