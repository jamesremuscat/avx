import logging


class VideoSwitcherController:

    def switch(self, deviceID, inChannel, outChannel):
        '''If a device with the given ID exists, perform a video switch. If not then return -1.'''
        if self.hasDevice(deviceID):
            logging.debug("Switching device " + deviceID + ": " + str(inChannel) + "=>" + str(outChannel))
            return self.devices[deviceID].sendInputToOutput(inChannel, outChannel)
        else:
            logging.warn("No device with ID " + deviceID)
            return -1
