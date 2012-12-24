class Controller(object):
    '''
    A Controller is essentially a bucket of devices, each identified with a string deviceID.
    '''
    pyroName = "aldates.alix.controller"

    def __init__(self):
        self.devices = {}
    
    def addDevice(self, device):
        self.devices[device.deviceID] = device
        
    def hasDevice(self, deviceID):
        return self.devices.has_key(deviceID)
        
    def switch(self, deviceID, inChannel, outChannel):
        '''If a device with the given ID exists, perform a video switch. If not then return -1.'''
        if self.devices.has_key(deviceID) :
            return self.devices[deviceID].sendInputToOutput(inChannel, outChannel)
        else:
            print "No device with ID " + deviceID
            return -1
        
    def move(self, camDeviceID, direction):
        if self.devices.has_key(camDeviceID):
            camera = self.devices[camDeviceID]
            if direction == CameraMove.Left:
                return camera.moveLeft()
            elif direction == CameraMove.Right:
                return camera.moveRight()
            elif direction == CameraMove.Up:
                return camera.moveUp()
            elif direction == CameraMove.Down:
                return camera.moveDown()
            elif direction == CameraMove.Stop:
                return camera.stop()
        else:
            print "No device with ID " + camDeviceID
        return -1
    
    def zoom(self, camDeviceID, zoomType):
        if self.devices.has_key(camDeviceID):
            camera = self.devices[camDeviceID]
            if zoomType == CameraZoom.Tele:
                return camera.zoomIn()
            elif zoomType == CameraZoom.Wide:
                return camera.zoomOut()
            elif zoomType == CameraZoom.Stop:
                return camera.zoomStop()
        else:
            print "No device with ID " + camDeviceID
        return -1
    
    def focus(self, camDeviceID, focusType):
        if self.devices.has_key(camDeviceID):
            camera = self.devices[camDeviceID]
            if focusType == CameraFocus.Auto:
                return camera.focusAuto()
            elif focusType == CameraFocus.Near:
                return camera.focusNear()
            elif focusType == CameraFocus.Far:
                return camera.focusFar()
            elif focusType == CameraFocus.Stop:
                return camera.focusStop()
        else:
            print "No device with ID " + camDeviceID
        return -1
    
    def exposure(self, camDeviceID, exposureType):
        if self.devices.has_key(camDeviceID):
            camera = self.devices[camDeviceID]
            if exposureType == CameraExposure.Brighter:
                return camera.brighter()
            elif exposureType == CameraExposure.Darker:
                return camera.darker()
            elif exposureType == CameraExposure.Auto:
                return camera.autoExposure()
        else:
            print "No device with ID " + camDeviceID
        return -1
            
    
    def savePreset(self, camDeviceID, preset):
        if self.devices.has_key(camDeviceID):
            camera = self.devices[camDeviceID]
            camera.storePreset(preset)
        else:
            print "No device with ID " + camDeviceID
        return -1
    
    def recallPreset(self, camDeviceID, preset):
        if self.devices.has_key(camDeviceID):
            camera = self.devices[camDeviceID]
            camera.recallPreset(preset)
        else:
            print "No device with ID " + camDeviceID
        return -1
    
    
class CameraMove():
    Left, Right, Up, Down, Stop = range(5)
    
class CameraZoom():
    Tele, Wide, Stop = range(3)
    
class CameraFocus():
    Near, Far, Auto, Stop = range(4)
    
class CameraExposure():
    Brighter, Darker, Auto = range(3)
    
