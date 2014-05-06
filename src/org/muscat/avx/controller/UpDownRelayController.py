from org.muscat.avx.controller.ControllerHelpers import deviceMethod
import logging


class UpDownRelayController:

    @deviceMethod
    def raiseUp(self, device, number):
        logging.debug("Raising " + device + ":" + str(number))
        d = self.devices[device]
        return d.raiseUp(number)

    @deviceMethod
    def lower(self, device, number):
        logging.debug("Lowering " + device + ":" + str(number))
        d = self.devices[device]
        return d.lower(number)

    @deviceMethod
    def stop(self, device, number):
        logging.debug("Stopping " + device + ":" + str(number))
        d = self.devices[device]
        return d.stop(number)
