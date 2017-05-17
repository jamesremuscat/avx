from avx.devices import Device
import colorsys
import logging
import socket
import time


class MiLight(Device):
    '''
    Control of MiLight / easybulb wifi lightbulbs
    '''

    socket = None

    def __init__(self, deviceID, ipAddress, port=8899, **kwargs):
        super(MiLight, self).__init__(deviceID, **kwargs)
        self.ipAddress = ipAddress
        self.port = port

    def initialise(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, message):
        if not self.socket:
            self.initialise()
        logging.debug("Sending " + message.encode('hex_codec') + " to " + self.ipAddress + ":" + str(self.port))
        self.socket.sendto(message, (self.ipAddress, self.port))

    def sendGroupOnAndWait(self, group):
        self.send(chr(groupID(group)) + "\x00\x55")
        time.sleep(0.1)

    def setColour(self, group, red, green, blue):
        self.sendGroupOnAndWait(group)
        self.send("\x40" + chr(rgbToMilight(red, green, blue)) + "\x55")

    def setWhite(self, group):
        self.sendGroupOnAndWait(group)
        self.send(chr(groupID(group) + 0x80) + "\x00\x55")

    def setBrightness(self, group, percentage):
        '''
        Set the brightness of the group, in their current mode.
        Percentage should be [0-100].
        '''
        self.sendGroupOnAndWait(group)
        self.send("\x4E" + chr(2 + int(percentage / 4)) + "\x55")

    def setOff(self, group):
        if group == 0:
            self.send("\x41\x00\x55")
        else:
            self.send(chr(groupID(group) + 1) + "\x00\x55")


def groupID(group):
    if group is 0:
        return 0x42
    else:
        return 67 + (2 * group)


def rgbToMilight(red, green, blue):
    '''
    This isn't quite right, and you can't do a proper conversion since milight requires a saturation of 1.
    Also, we throw away the value - we just extract the hue of the rgb colour and try to map that to the
    milight colour chart.
    '''
    hsv = colorsys.rgb_to_hsv(red, green, blue)
    hue = hsv[0] * 360
    milight = ((250 - hue) % 360) * 256 / 360
    return int(round(milight))
