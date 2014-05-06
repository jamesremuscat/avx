from org.muscat.avx.controller.ControllerHelpers import deviceMethod
import logging
from org.muscat.avx.controller.ControllerHttp import httpAccessible


class RelayController:

    @deviceMethod
    @httpAccessible
    def turnOn(self, device, number):
        logging.debug("Turning on " + device + ":" + str(number))
        d = self.devices[device]
        return d.on(number)

    @deviceMethod
    @httpAccessible
    def turnOff(self, device, number):
        logging.debug("Turning off " + device + ":" + str(number))
        d = self.devices[device]
        return d.off(number)
