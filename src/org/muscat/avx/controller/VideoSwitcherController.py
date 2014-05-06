import logging
from org.muscat.avx.controller.ControllerHelpers import deviceMethod


class VideoSwitcherController:

    @deviceMethod
    def switch(self, deviceID, inChannel, outChannel):
        logging.info("Switching device " + deviceID + ": " + str(inChannel) + "=>" + str(outChannel))
        return self.devices[deviceID].sendInputToOutput(inChannel, outChannel)
