'''
Created on 13 Nov 2012

@author: james
'''
from org.muscat.staldates.aldatesx.devices.SerialDevice import SerialDevice

class VISCACamera(SerialDevice):
    '''
    A camera controlled by the Sony VISCA protocol e.g. Sony D31,
    '''
    
    # Pan/tilt speeds can vary from 0x01 - 0x18; AMX uses 0x06
    panSpeed = 0x06
    tiltSpeed = 0x06
    
    # Zoom speed can vary from 0x02-0x07
    zoomSpeed = 0x06

    def __init__(self, deviceID, serialDevice, cameraID):
        super(VISCACamera, self).__init__(deviceID, serialDevice)
        self.cameraID = cameraID
        
    def sendVISCA(self, commandBytes):
        return self.sendCommand(SerialDevice.byteArrayToString([0x80 + self.cameraID] + commandBytes + [0xFF]))
        
    def moveUp(self):
        return self.sendVISCA([0x01, 0x06, 0x01, self.panSpeed, self.tiltSpeed, 0x03, 0x01])
        
    def moveDown(self):
        return self.sendVISCA([0x01, 0x06, 0x01, self.panSpeed, self.tiltSpeed, 0x03, 0x02])
        
    def moveLeft(self):
        return self.sendVISCA([0x01, 0x06, 0x01, self.panSpeed, self.tiltSpeed, 0x01, 0x03])
        
    def moveRight(self):
        return self.sendVISCA([0x01, 0x06, 0x01, self.panSpeed, self.tiltSpeed, 0x02, 0x03])
        
    def stop(self):
        return self.sendVISCA([0x01, 0x06, 0x01, self.panSpeed, self.tiltSpeed, 0x03, 0x03])
        
    def zoomIn(self):
        return self.sendVISCA([0x01, 0x04, 0x07, 0x20 + self.zoomSpeed])
        
    def zoomOut(self):
        return self.sendVISCA([0x01, 0x04, 0x07, 0x30 + self.zoomSpeed])
        
    def zoomStop(self):
        return self.sendVISCA([0x01, 0x04, 0x07, 0x00])
        
    def focusFar(self):
        self.focusManual()
        return self.sendVISCA([0x01, 0x04, 0x08, 0x02])
        
    def focusNear(self):
        self.focusManual()
        return self.sendVISCA([0x01, 0x04, 0x08, 0x03])
        
    def focusStop(self):
        return self.sendVISCA([0x01, 0x04, 0x08, 0x00])
        
    def focusAuto(self):
        return self.sendVISCA([0x01, 0x04, 0x38, 0x02])
        
    def focusManual(self):
        return self.sendVISCA([0x01, 0x04, 0x38, 0x03])
    
    def brighter(self):
        self.sendVISCA([0x01, 0x04, 0x39, 0x0D]) # Put camera into manual exposure mode first!
        return self.sendVISCA([0x01, 0x04, 0x0D, 0x02])
    
    def darker(self):
        self.sendVISCA([0x01, 0x04, 0x39, 0x0D]) # Put camera into manual exposure mode first!
        return self.sendVISCA([0x01, 0x04, 0x0D, 0x03])
    
    def autoExposure(self):
        return self.sendVISCA([0x01, 0x04, 0x39, 0x00])
    
    def backlightCompOn(self):
        return self.sendVISCA([0x01, 0x04, 0x33, 0x02])
    
    def backlightCompOff(self):
        return self.sendVISCA([0x01, 0x04, 0x33, 0x03])
        
    def storePreset(self, preset):
        if preset < 0 or preset > 5:
            return -1
        self.sendVISCA([0x01, 0x04, 0x3F, 0x01, preset])
        
    def recallPreset(self, preset):
        if preset < 0 or preset > 5:
            return -1
        self.sendVISCA([0x01, 0x04, 0x3F, 0x02, preset])
        
        
        