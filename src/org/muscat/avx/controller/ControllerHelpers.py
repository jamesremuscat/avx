import logging

def deviceMethod(originalFunc):
    def dmFunc(selff, deviceID, *args, **kwargs):
        if selff.hasDevice(deviceID):
            return originalFunc(selff, deviceID, *args, **kwargs)
        else:
            for slave in selff.slaves:
                if slave.hasDevice(deviceID):
                    methodName = originalFunc.__name__
                    # Make the same call to our slave as was made to us
                    return getattr(slave, methodName)(deviceID, *args, **kwargs)

            logging.warn("No device with ID " + deviceID)
            return -1
    return dmFunc