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
        self.sendCommand("Mode = 3\x13")
        
    def overlayOff(self):
        self.sendCommand("Mode = 0\x13")
        
    def fadeOut(self):
        self.sendCommand("Fade = 0\x13")
        
    def fadeIn(self):
        self.sendCommand("Fade = 1\x13")
    
    def freeze(self):
        self.sendCommand("Freeze = On\x13")
    
    def unfreeze(self):
        self.sendCommand("Freeze = Off\x13")