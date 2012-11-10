
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
            return -1
            