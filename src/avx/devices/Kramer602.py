'''
Created on 13 Nov 2012

@author: jrem
'''
from avx.devices.SerialDevice import SerialDevice,\
    SerialListener
import logging


class Kramer602(SerialDevice):
    '''
    The Kramer 602 (preview) switcher. Reverse-engineered from the AMX code, this is apparently not Protocol 2000...
    '''

    def __init__(self, deviceID, serialDevice, **kwargs):
        super(Kramer602, self).__init__(deviceID, serialDevice, 1200, **kwargs)

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


class Kramer602Listener(SerialListener):
    ''' Class to listen to and interpret incoming messages from a Kramer 602. '''

    dispatchers = []

    def __init__(self, deviceID, parent, controller, machineNumber=1):
        ''' Initialise this Kramer602 listener. port should be the same Serial that's already been passed to a Kramer602. '''
        super(Kramer602Listener, self).__init__(deviceID, controller.getDevice(parent), messageSize=2)
        self.machineNumber = machineNumber

    def process(self, message):
        logging.debug("Received from Kramer 602: " + SerialDevice.byteArrayToString(message).encode('hex_codec'))
        if ((message[0] & 0x7) == (self.machineNumber - 1)):
            if message[1] == 0xff:  # Occasionally on startup we seem to receive a three-byte packet with the middle byte 0xFF. So ignore that middle.
                message[1] = self.parentDevice.port.read(1)
            if (message[1] & 0x20) == 0:  # Not just a "I switched successfully" message
                outp = (((message[1] & 0x1F) - 1) % 2) + 1
                inp = (((message[1] & 0x1F) - outp) / 2) + 1  # int(math.ceil((message[1] & 0x1F) + (2 / 2)) - 1)
                for d in self.dispatchers:
                    d.updateOutputMappings({self.parentDevice.deviceID: {outp: inp}})
            else:
                self.parentDevice.requestStatus()  # Request device to send current status so listener can intercept
