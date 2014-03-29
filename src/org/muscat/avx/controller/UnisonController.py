import logging


class UnisonController:
    def activate(self, device, objectID):
        def reallyActivate():
            logging.debug("Activating preset " + objectID + " on " + device)
            d = self.devices[device]
            return d.activate(objectID)
        return self.withDevice(device, reallyActivate)

    def deactivate(self, device, objectID):
        def reallyDeactivate():
            logging.debug("Deactivating preset " + objectID + " on " + device)
            d = self.devices[device]
            return d.deactivate(objectID)
        return self.withDevice(device, reallyDeactivate)
