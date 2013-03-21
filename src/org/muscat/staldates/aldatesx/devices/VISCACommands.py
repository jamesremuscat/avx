'''
Created on 21 Mar 2013

@author: jrem
'''

class VISCACommand(object):
    '''
    Encapsulates a VISCA command.
    '''

    def __init__(self, cameraID = 1):
        self.cameraID = cameraID
        
    def getBytes(self):
        return [0x80 + self.cameraID] + self.getInnerBytes() + [0xFF]
    

# CAM_Zoom
class ZoomStop(VISCACommand):
    def getInnerBytes(self):
        return [0x01, 0x04, 0x07, 0x00]
        
class ZoomIn(VISCACommand):
    
    def __init__(self, speed = 2, cameraID = 1):
        super(ZoomIn, self).__init__(cameraID)
        if 1 < speed < 8:
            self.speed = speed
        else:
            self.speed = 2
    
    def getInnerBytes(self):
        return [0x01, 0x04, 0x07, 0x20 + self.speed]
    
class ZoomOut(VISCACommand):
    
    def __init__(self, speed = 2, cameraID = 1):
        super(ZoomIn, self).__init__(cameraID)
        if 1 < speed < 8:
            self.speed = speed
        else:
            self.speed = 2
    
    def getInnerBytes(self):
        return [0x01, 0x04, 0x07, 0x30 + self.speed]
    
    
# CAM_Focus
class FocusStop(VISCACommand):
    def getInnerBytes(self):
        return [0x01, 0x04, 0x08, 0x00]
    
class FocusFar(VISCACommand):
    def getInnerBytes(self):
        return [0x01, 0x04, 0x08, 0x02]
    
class FocusNear(VISCACommand):
    def getInnerBytes(self):
        return [0x01, 0x04, 0x08, 0x03]
    
class FocusAuto(VISCACommand):
    def getInnerBytes(self):
        return [0x01, 0x04, 0x38, 0x02]
    
class FocusManual(VISCACommand):
    def getInnerBytes(self):
        return [0x01, 0x04, 0x38, 0x03]
    
# CAM_Memory
class MemorySet(VISCACommand):
    
    def __init__(self, preset, cameraID = 1):
        super(MemorySet, self).__init__(cameraID)
        self.preset = preset
    
    def getInnerBytes(self):
        return [0x01, 0x04, 0x3F, 0x01, self.preset]
    
class MemoryRecall(VISCACommand):
    
    def __init__(self, preset, cameraID = 1):
        super(MemorySet, self).__init__(cameraID)
        self.preset = preset
    
    def getInnerBytes(self):
        return [0x01, 0x04, 0x3F, 0x02, self.preset]

# Pan-tiltDrive

class MoveUp(VISCACommand):
    def __init__(self, speed, cameraID = 1):
        super(MoveUp, self).__init__(cameraID)
        self.speed = speed
