import logging


class UpDownRelayController:
    def raiseUp(self, device, number):
        def reallyRaise():
            logging.debug("Raising " + device + ":" + str(number))
            d = self.devices[device]
            d.raiseUp(number)
        return self.withDevice(device, reallyRaise)

    def lower(self, device, number):
        def reallyLower():
            logging.debug("Lowering " + device + ":" + str(number))
            d = self.devices[device]
            d.lower(number)
        return self.withDevice(device, reallyLower)

    def stop(self, device, number):
        def reallyStop():
            logging.debug("Stopping " + device + ":" + str(number))
            d = self.devices[device]
            d.stop(number)
        return self.withDevice(device, reallyStop)
