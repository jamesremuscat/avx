'''
Created on 13 Nov 2012

@author: jrem
'''
from org.muscat.staldates.aldatesx.devices.SerialDevice import SerialDevice

class Kramer602(SerialDevice):
    '''
    The Kramer 602 (preview) switcher. Reverse-engineered from the AMX code, this is apparently not Protocol 2000...
    '''


    def __init__(self, deviceID, serialDevice):
        super(Kramer602, self).__init__(deviceID, serialDevice)
        
    def sendInputToOutput(self, inChannel, outChannel):
        code = [0, (2 * inChannel) - (2 - outChannel)]
        self.sendCommand(SerialDevice.byteArrayToString(code))