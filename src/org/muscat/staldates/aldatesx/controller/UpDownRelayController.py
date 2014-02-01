import logging


class UpDownRelayController:
    def raiseUp(self, device, number):
        if self.hasDevice(device):
            logging.debug("Raising " + device + ":" + str(number))
            d = self.devices[device]
            d.raiseUp(number)
        else:
            logging.warn("No device with ID " + device)
        return -1

    def lower(self, device, number):
        if self.hasDevice(device):
            logging.debug("Lowering " + device + ":" + str(number))
            d = self.devices[device]
            d.lower(number)
        else:
            logging.warn("No device with ID " + device)
        return -1

    def stop(self, device, number):
        if self.hasDevice(device):
            logging.debug("Stopping " + device + ":" + str(number))
            d = self.devices[device]
            d.stop(number)
        else:
            logging.warn("No device with ID " + device)
        return -1
