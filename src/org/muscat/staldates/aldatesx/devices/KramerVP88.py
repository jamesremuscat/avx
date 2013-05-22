'''
Created on 10 Nov 2012

@author: james
'''
from org.muscat.staldates.aldatesx.devices.SerialDevice import SerialDevice, SerialListener


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


class KramerVP88Listener(SerialListener):
    ''' Class to listen to and interpret incoming messages from a VP88. '''

    dispatchers = []

    def __init__(self, port, machineNumber=1):
        ''' Initialise this KramerVP88 listener. port should be the same Serial that's already been passed to a KramerVP88. '''
        super(KramerVP88Listener, self).__init__(port)
        self.machineNumber = machineNumber

    def process(self, message):
        if (message[3] == 0x80 + self.machineNumber):
            if (message[0] == 0x41) or (message[0] == 0x45):  # Notification of video switch or response to query
                inp = message[1] - 0x80
                outp = message[2] - 0x80
                return {outp: inp}
        return {}
