'''
Created on 10 Nov 2012

@author: james
'''
from org.muscat.staldates.aldatesx.devices.SerialDevice import SerialDevice


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
