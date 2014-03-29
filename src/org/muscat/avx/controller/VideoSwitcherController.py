import logging


class VideoSwitcherController:

    def switch(self, deviceID, inChannel, outChannel):
        def reallySwitch():
            logging.info("Switching device " + deviceID + ": " + str(inChannel) + "=>" + str(outChannel))
            return self.devices[deviceID].sendInputToOutput(inChannel, outChannel)
        return self.withDevice(deviceID, reallySwitch)
