'''
Created on 13 Nov 2012

@author: james
'''
from org.muscat.staldates.aldatesx.devices.SerialDevice import SerialDevice

class VISCACamera(SerialDevice):
    '''
    A camera controlled by the Sony VISCA protocol e.g. Sony D31,
    '''
    
    # Speeds can vary from 0x01 - 0x18; AMX uses 0x06
    panSpeed = 0x06
    tiltSpeed = 0x06

    def __init__(self, deviceID, serialDevice, cameraID):
        super(VISCACamera, self).__init__(deviceID, serialDevice)
        self.cameraID = cameraID
        
    def sendVISCA(self, commandBytes):
        self.sendCommand(SerialDevice.byteArrayToString([0x80 + self.cameraID] + commandBytes + [0xFF]))
        
    def moveUp(self):
        self.sendVISCA([0x01, 0x06, 0x01, self.panSpeed, self.tiltSpeed, 0x03, 0x01])
        
    def moveDown(self):
        self.sendVISCA([0x01, 0x06, 0x01, self.panSpeed, self.tiltSpeed, 0x03, 0x02])
        
    def moveLeft(self):
        self.sendVISCA([0x01, 0x06, 0x01, self.panSpeed, self.tiltSpeed, 0x01, 0x03])
        
    def moveRight(self):
        self.sendVISCA([0x01, 0x06, 0x01, self.panSpeed, self.tiltSpeed, 0x02, 0x03])
        
    def stop(self):
        self.sendVISCA([0x01, 0x06, 0x01, self.panSpeed, self.tiltSpeed, 0x03, 0x03])
        
    def zoomIn(self):
        self.sendVISCA([0x01, 0x04, 0x07, 0x02])
        
    def zoomOut(self):
        self.sendVISCA([0x01, 0x04, 0x07, 0x03])
        
    def zoomStop(self):
        self.sendVISCA([0x01, 0x04, 0x07, 0x00])
        
    def focusFar(self):
        self.focusManual()
        self.sendVISCA([0x01, 0x04, 0x08, 0x02])
        
    def focusNear(self):
        self.focusManual()
        self.sendVISCA([0x01, 0x04, 0x08, 0x03])
        
    def focusStop(self):
        self.sendVISCA([0x01, 0x04, 0x08, 0x00])
        
    def focusAuto(self):
        self.sendVISCA([0x01, 0x04, 0x38, 0x02])
        
    def focusManual(self):
        self.sendVISCA([0x01, 0x04, 0x38, 0x03])
        
        
        