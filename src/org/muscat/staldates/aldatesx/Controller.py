
class Controller(object):
    '''
    A Controller is essentially a bucket of devices, each identified with a string deviceID.
    '''

    def __init__(self):
        self.devices = {}
    
    def addDevice(self, device):
        self.devices[device.deviceID] = device
        
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
    
    
class CameraMove():
    Left, Right, Up, Down, Stop = range(5)