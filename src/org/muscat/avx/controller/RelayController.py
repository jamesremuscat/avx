from org.muscat.avx.controller.ControllerHelpers import deviceMethod
import logging


class RelayController:

    @deviceMethod
    def turnOn(self, device, number):
        logging.debug("Turning on " + device + ":" + str(number))
        d = self.devices[device]
        return d.on(number)

    @deviceMethod
    def turnOff(self, device, number):
        logging.debug("Turning off " + device + ":" + str(number))
        d = self.devices[device]
        return d.off(number)
