'''
Created on 13 Nov 2012

@author: jrem
'''
from avx.devices.serial import SerialDevice


class CoriogenEclipse(SerialDevice):
    '''
    Coriogen Eclipse scan converter/genlock/overlay
    '''

    def __init__(self, deviceID, serialDevice, **kwargs):
        super(CoriogenEclipse, self).__init__(deviceID, serialDevice, **kwargs)

    def overlayOn(self):
        self.sendCommand("Mode = 3\r\n")

    def overlayOff(self):
        self.sendCommand("Mode = 0\r\n")

    def fadeOut(self):
        self.sendCommand("Fade = 0\r\n")

    def fadeIn(self):
        self.sendCommand("Fade = 1\r\n")

    def freeze(self):
        self.sendCommand("Freeze = On\r\n")

    def unfreeze(self):
        self.sendCommand("Freeze = Off\r\n")

    def overscanOn(self):
        self.sendCommand("Overscan = On\r\n")

    def overscanOff(self):
        self.sendCommand("Overscan = Off\r\n")
