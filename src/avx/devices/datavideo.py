from avx.devices.net.dvip import DVIPCamera
from avx.devices.serial.VISCACamera import VISCACamera


class _PTC150Base(object):
    '''
    Datavideo PTC-150, with some variations on VISCA.
    '''

    MAX_PAN_SPEED = 0x18
    MAX_TILT_SPEED = 0x18
    MIN_ZOOM_SPEED = 0x01
    MAX_ZOOM_SPEED = 0x07
    MAX_PRESETS = 51  # as it's zero-indexed


class PTC150(_PTC150Base, VISCACamera):
    def tallyRed(self):
        self.sendVISCA([0x01, 0x7E, 0x01, 0x0A, 0x00, 0x02, 0x00])

    def tallyGreen(self):
        self.sendVISCA([0x01, 0x7E, 0x01, 0x0A, 0x00, 0x03, 0x02])

    def tallyOff(self):
        self.sendVISCA([0x01, 0x7E, 0x01, 0x0A, 0x00, 0x03])


class PTC150_DVIP(_PTC150Base, DVIPCamera):
    def _tally(self, red, green):
        self.sendVISCA([0x01, 0x7E, 0x01, 0x0A, 0x00, 0x02 * red, 0x02 * green])

    def tallyRed(self):
        self._tally(True, False)

    def tallyGreen(self):
        self._tally(False, True)

    def tallyOff(self):
        self._tally(False, False)


__all__ = [
    PTC150,
    PTC150_DVIP
]
