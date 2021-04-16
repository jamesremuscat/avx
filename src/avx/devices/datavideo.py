from avx.devices.net.dvip import DVIPCamera
from avx.devices.serial.VISCACamera import CameraSettingEnum, VISCACamera
from enum import Enum


class _PTC150Base(object):
    '''
    Datavideo PTC-150, with some variations on VISCA.
    '''

    MAX_PAN_SPEED = 0x18
    MAX_TILT_SPEED = 0x18
    MIN_ZOOM_SPEED = 0x01
    MAX_ZOOM_SPEED = 0x07
    MAX_PRESETS = 51  # as it's zero-indexed

    def setAperture(self, aperture):
        if isinstance(aperture, Aperture):
            av = aperture.code
        else:
            av = aperture
        self.sendVISCA([0x01, 0x04, 0x4D,  # It's this byte that differs from Sony (0x4B) and docs
                        (av & 0xF000) >> 12,
                        (av & 0x0F00) >> 8,
                        (av & 0x00F0) >> 4,
                        (av & 0x000F)])


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


class Aperture(CameraSettingEnum):
    CLOSE = (0x00, "Closed")
    F14 = (0x05, "F14")
    F11 = (0x06, "F11")
    F9_6 = (0x07, "F9.6")
    F8 = (0x08, "F8")
    F6_8 = (0x09, "F6.8")
    F5_6 = (0x0A, "F5.6")
    F4_8 = (0x0B, "F4.8")
    F4 = (0x0C, "F4")
    F3_4 = (0x0D, "F3.4")
    F2_8 = (0x0E, "F2.8")
    F2_4 = (0x0F, "F2.4")
    F2 = (0x10, "F2")
    F1_6 = (0x11, "F1.6")


class Shutter(CameraSettingEnum):
    T1 = (0x00, "1s")
    T2 = (0x01, "1/2s")
    T3 = (0x02, "1/3s")
    T6 = (0x03, "1/6s")
    T12 = (0x04, "1/12s")
    T25 = (0x05, "1/25s")
    T50 = (0x06, "1/50s")
    T75 = (0x07, "1/75s")
    T100 = (0x08, "1/100s")
    T120 = (0x09, "1/120s")
    T150 = (0x0A, "1/150s")
    T215 = (0x0B, "1/215s")
    T300 = (0x0C, "1/300s")
    T425 = (0x0D, "1/425s")
    T600 = (0x0E, "1/600s")
    T1000 = (0x0F, "1/1000s")
    T1250 = (0x10, "1/1250s")
    T1750 = (0x11, "1/1750s")
    T2500 = (0x12, "1/2500s")
    T3500 = (0x13, "1/3500s")
    T6000 = (0x14, "1/6000s")
    T10000 = (0x15, "1/10000s")


class Gain(CameraSettingEnum):
    G_0 = (0x01, "0")
    G_2 = (0x02, "2")
    G_4 = (0x03, "4")
    G_6 = (0x04, "6")
    G_8 = (0x05, "8")
    G_10 = (0x06, "10")
    G_12 = (0x07, "12")
    G_14 = (0x08, "14")
    G_16 = (0x09, "16")
    G_18 = (0x0A, "18")
    G_20 = (0x0B, "20")
    G_22 = (0x0C, "22")
    G_24 = (0x0D, "24")
    G_26 = (0x0E, "26")
    G_28 = (0x0F, "28")


__all__ = [
    PTC150,
    PTC150_DVIP,
    Aperture,
    Shutter,
    Gain
]
