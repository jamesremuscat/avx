import logging
from org.muscat.avx.controller.ControllerHelpers import deviceMethod
from org.muscat.avx.controller.ControllerHttp import httpAccessible


class VideoSwitcherController:

    @deviceMethod
    @httpAccessible
    def switch(self, deviceID, inChannel, outChannel):
        logging.info("Switching device " + deviceID + ": " + str(inChannel) + "=>" + str(outChannel))
        return self.devices[deviceID].sendInputToOutput(inChannel, outChannel)
