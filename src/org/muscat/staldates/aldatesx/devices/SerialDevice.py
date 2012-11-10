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
        self.port.write(commandString)
        