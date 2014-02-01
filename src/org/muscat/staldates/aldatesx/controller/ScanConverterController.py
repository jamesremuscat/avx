import logging


class ScanConverterController:
    def toggleOverscan(self, scDevice, overscan):
        if self.hasDevice(scDevice):
            sc = self.devices[scDevice]
            if overscan:
                sc.overscanOn()
            else:
                sc.overscanOff()
        else:
            logging.warn("No device with ID " + scDevice)
        return -1

    def toggleFreeze(self, scDevice, freeze):
        if self.hasDevice(scDevice):
            sc = self.devices[scDevice]
            if freeze:
                sc.freeze()
            else:
                sc.unfreeze()
        else:
            logging.warn("No device with ID " + scDevice)
        return -1

    def toggleOverlay(self, scDevice, overlay):
        if self.hasDevice(scDevice):
            sc = self.devices[scDevice]
            if overlay:
                sc.overlayOn()
            else:
                sc.overlayOff()
        else:
            logging.warn("No device with ID " + scDevice)
        return -1

    def toggleFade(self, scDevice, fade):
        if self.hasDevice(scDevice):
            sc = self.devices[scDevice]
            if fade:
                sc.fadeOut()
            else:
                sc.fadeIn()
        else:
            logging.warn("No device with ID " + scDevice)
        return -1

    def recalibrate(self, scDevice):
        if self.hasDevice(scDevice):
            sc = self.devices[scDevice]
            sc.recalibrate()
        else:
            logging.warn("No device with ID " + scDevice)
        return -1
