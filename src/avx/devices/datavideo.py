from avx.devices.serial.VISCACamera import VISCACamera
from avx.devices.Device import InvalidArgumentException


class PTC150(VISCACamera):
    '''
    Datavideo PTC-150, with some variations on VISCA.
    '''

    def storePreset(self, preset):
        if preset > 0 and preset <= 50:
            self.sendVISCA([0x01, 0x04, 0x3F, 0x01, preset])
        else:
            raise InvalidArgumentException("Preset out of range (1-50)")

    def recallPreset(self, preset):
        if preset > 0 and preset <= 50:
            self.sendVISCA([0x01, 0x04, 0x3F, 0x02, preset])
        else:
            raise InvalidArgumentException("Preset out of range (1-50)")

    def tallyRed(self):
        self.sendVISCA([0x01, 0x7E, 0x01, 0x0A, 0x00, 0x02, 0x00])

    def tallyGreen(self):
        self.sendVISCA([0x01, 0x7E, 0x01, 0x0A, 0x00, 0x03, 0x02])

    def tallyOff(self):
        self.sendVISCA([0x01, 0x7E, 0x01, 0x0A, 0x00, 0x03])
