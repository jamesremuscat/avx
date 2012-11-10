
class Controller(object):
    '''
    A Controller is essentially a bucket of devices, each identified with a string deviceID.
    '''

    def __init__(self):
        self.devices = {}
        
    def getDevices(self):
        return self.devices.values()
    
    def getDevice(self, deviceID):
        return self.devices[deviceID]
    
    def addDevice(self, device):
        self.devices[device.deviceID] = device