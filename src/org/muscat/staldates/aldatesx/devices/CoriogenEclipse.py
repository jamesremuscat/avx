'''
Created on 13 Nov 2012

@author: jrem
'''
from org.muscat.staldates.aldatesx.devices.SerialDevice import SerialDevice

class CoriogenEclipse(SerialDevice):
    '''
    Coriogen Eclipse scan converter/genlock/overlay
    '''


    def __init__(self, serialDevice):
        super(CoriogenEclipse, self).__init__(1, serialDevice)

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
