import logging


class UnisonController:
    def activate(self, device, objectID):
        if self.hasDevice(device):
            logging.debug("Activating preset " + objectID + " on " + device)
            d = self.devices[device]
            d.activate(objectID)
        else:
            logging.warn("No device with ID " + device)
        return -1

    def deactivate(self, device, objectID):
        if self.hasDevice(device):
            logging.debug("Deactivating preset " + objectID + " on " + device)
            d = self.devices[device]
            d.deactivate(objectID)
        else:
            logging.warn("No device with ID " + device)
        return -1
