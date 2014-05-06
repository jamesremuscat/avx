from org.muscat.avx.controller.ControllerHelpers import deviceMethod
import logging
from org.muscat.avx.controller.ControllerHttp import httpAccessible


class UpDownRelayController:

    @deviceMethod
    @httpAccessible
    def raiseUp(self, device, number):
        logging.debug("Raising " + device + ":" + str(number))
        d = self.devices[device]
        return d.raiseUp(number)

    @deviceMethod
    @httpAccessible
    def lower(self, device, number):
        logging.debug("Lowering " + device + ":" + str(number))
        d = self.devices[device]
        return d.lower(number)

    @deviceMethod
    @httpAccessible
    def stop(self, device, number):
        logging.debug("Stopping " + device + ":" + str(number))
        d = self.devices[device]
        return d.stop(number)
