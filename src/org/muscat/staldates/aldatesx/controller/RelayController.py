import logging


class RelayController:

    def turnOn(self, device, number):
        def reallyTurnOn():  # ahem
            logging.debug("Turning on " + device + ":" + str(number))
            d = self.devices[device]
            return d.on(number)
        return self.withDevice(device, reallyTurnOn)

    def turnOff(self, device, number):
        def reallyTurnOff():
            logging.debug("Turning off " + device + ":" + str(number))
            d = self.devices[device]
            return d.off(number)
        return self.withDevice(device, reallyTurnOff)
