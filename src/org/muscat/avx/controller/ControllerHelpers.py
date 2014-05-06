import logging


def deviceMethod(originalFunc):
    '''
    Decorator function that augments a method operating on a device with
    a check that the device exists, and calls the corresponding method on
    remote slaves if the device exists there.

    The first (non-self) argument to the function MUST be the device ID.

    This decorator preserves the func_dict of the original function.
    '''
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

    dmFunc.func_dict = originalFunc.func_dict

    return dmFunc
