import logging


class RelayController:

    def turnOn(self, device, number):
        if self.hasDevice(device):
            logging.debug("Turning on " + device + ":" + str(number))
            d = self.devices[device]
            d.on(number)
        else:
            logging.warn("No device with ID " + device)
        return -1

    def turnOff(self, device, number):
        if self.hasDevice(device):
            logging.debug("Turning off " + device + ":" + str(number))
            d = self.devices[device]
            d.off(number)
        else:
            logging.warn("No device with ID " + device)
        return -1
