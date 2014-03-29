

class ScanConverterController:
    def toggleOverscan(self, scDevice, overscan):
        def reallyOverscan():
            sc = self.devices[scDevice]
            if overscan:
                return sc.overscanOn()
            else:
                return sc.overscanOff()
        return self.withDevice(scDevice, reallyOverscan)

    def toggleFreeze(self, scDevice, freeze):
        def reallyFreeze():
            sc = self.devices[scDevice]
            if freeze:
                return sc.freeze()
            else:
                return sc.unfreeze()
        return self.withDevice(scDevice, reallyFreeze)

    def toggleOverlay(self, scDevice, overlay):
        def reallyOverlay():
            sc = self.devices[scDevice]
            if overlay:
                return sc.overlayOn()
            else:
                return sc.overlayOff()
        return self.withDevice(scDevice, reallyOverlay)

    def toggleFade(self, scDevice, fade):
        def reallyFade():
            sc = self.devices[scDevice]
            if fade:
                return sc.fadeOut()
            else:
                return sc.fadeIn()
        return self.withDevice(scDevice, reallyFade)

    def recalibrate(self, scDevice):
        def reallyRecalibrate():
            sc = self.devices[scDevice]
            return sc.recalibrate()
        return self.withDevice(scDevice, reallyRecalibrate)
