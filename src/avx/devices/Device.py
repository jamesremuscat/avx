import logging


class Device(object):
    '''
    This is a thing. It does stuff.
    '''

    def __init__(self, deviceID, httpAccessible=False, **kwargs):
        self.deviceID = deviceID
        self.httpAccessible = httpAccessible
        self.log = logging.getLogger(deviceID)

    def initialise(self):
        '''
        Extension point for device-specific initialisation code (e.g. resetting to known-default config)
        '''
        pass

    def deinitialise(self):
        '''
        Extension point for device-specific deinitialisation code (e.g. closing open file handles)
        '''
        pass

    def broadcast(self, msgType, data):
        '''
        This method is automatically overridden when a device is added to a Controller.
        '''
        pass

    @staticmethod
    def create(d, controller):
        deviceID = d["deviceID"]
        logging.info("Creating device " + deviceID)
        if "options" in d:
            return get_class(d["class"])(deviceID, controller=controller, **d["options"])
        else:
            return get_class(d["class"])(deviceID, controller=controller)


def get_class(kls):
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    m = __import__(module)
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m


class InvalidArgumentException(Exception):
    pass
