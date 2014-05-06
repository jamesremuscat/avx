from org.muscat.avx.controller.ControllerHelpers import deviceMethod
import logging


class UnisonController:

    @deviceMethod
    def activate(self, device, objectID):
        logging.debug("Activating preset " + objectID + " on " + device)
        d = self.devices[device]
        return d.activate(objectID)

    @deviceMethod
    def deactivate(self, device, objectID):
        logging.debug("Deactivating preset " + objectID + " on " + device)
        d = self.devices[device]
        return d.deactivate(objectID)
