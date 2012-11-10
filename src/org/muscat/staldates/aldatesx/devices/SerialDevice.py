from org.muscat.staldates.aldatesx.devices.Device import Device
from serial import Serial

class SerialDevice(Device):
    '''
    A device we connect to over a serial port.
    '''

    def __init__(self, deviceID, serialDevice):
        super(SerialDevice, self).__init__(deviceID)
        self.port = Serial(serialDevice)
        
    def sendCommand(self, commandString):
        print "Sending " + commandString.encode('hex_codec')
        sentBytes = self.port.write(commandString)
        print str(sentBytes) + " bytes sent"
        
    @staticmethod
    def byteArrayToString(byteArray):
        return ''.join(chr(b) for b in byteArray)
        