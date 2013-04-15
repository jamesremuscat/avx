

class Device(object):
    '''
    This is a thing. It does stuff.
    '''

    def __init__(self, deviceID):
        self.deviceID = deviceID

    def initialise(self):
        '''
        Extension point for device-specific initialisation code (e.g. resetting to known-default config)
        '''
        pass
