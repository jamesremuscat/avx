import logging


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

    @staticmethod
    def create(d, controller):
        deviceID = d["deviceID"]
        logging.info("Creating device " + deviceID)
        return get_class(d["class"])(deviceID, controller=controller, **d["options"])


def get_class(kls):
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    m = __import__(module)
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m
