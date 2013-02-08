from org.muscat.staldates.aldatesx.devices.Device import Device
from serial import Serial
import logging

class SerialDevice(Device):
    '''
    A device we connect to over a serial port.
    '''

    def __init__(self, deviceID, serialDevice, baud=9600):
        '''
        Create a SerialDevice with a given device ID, using a new Serial with the given device address
        (e.g. "/dev/ttyUSB0") if given as a string, else assume serialDevice is a Serial and use that.
        '''
        super(SerialDevice, self).__init__(deviceID)
        if isinstance(serialDevice, str):
            self.port = Serial(serialDevice, baud)
        else:
            self.port = serialDevice
        
    def sendCommand(self, commandString):
        logging.debug("Sending " + commandString.encode('hex_codec') + " to " + self.port.portstr)
        sentBytes = self.port.write(commandString)
        logging.debug(str(sentBytes) + " bytes sent")
        return sentBytes
        
    @staticmethod
    def byteArrayToString(byteArray):
        return ''.join(chr(b) for b in byteArray)
        