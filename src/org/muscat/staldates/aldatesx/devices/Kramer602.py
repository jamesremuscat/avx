'''
Created on 13 Nov 2012

@author: jrem
'''
from org.muscat.staldates.aldatesx.devices.SerialDevice import SerialDevice
import logging


class Kramer602(SerialDevice):
    '''
    The Kramer 602 (preview) switcher. Reverse-engineered from the AMX code, this is apparently not Protocol 2000...
    '''

    def __init__(self, deviceID, serialDevice):
        super(Kramer602, self).__init__(deviceID, serialDevice, 1200)

    def sendInputToOutput(self, inChannel, outChannel):
        if outChannel > 2:
            logging.error("Output channel " + str(outChannel) + " does not exist on switcher " + self.deviceID)
        else:
            code = [0, 0x80 + (2 * inChannel) - (2 - outChannel)]
            self.sendCommand(SerialDevice.byteArrayToString(code))
