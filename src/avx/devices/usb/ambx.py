'''
Heavily borrowing from https://bitbucket.org/wump/ambx-python/ and https://code.google.com/p/combustd before it
'''

from avx.devices import Device
import usb
from array import array


# USB identification
VENDOR = 0x0471
PRODUCT = 0x083f

# Endpoints
EP_IN = 0x81
EP_OUT = 0x02
EP_PNP = 0x83

# Packet start
PKT_HEADER = 0xA1

# -- Commands --
SET_LIGHT_COLOR = 0x03
SET_TIMED_COLOR_SEQUENCE = 0x72  # Not used


# -- Lights --
class Lights:
    LEFT = 0x0B
    RIGHT = 0x1B
    WWLEFT = 0x2B
    WWCENTER = 0x3B
    WWRIGHT = 0x4B


class AMBX(Device):
    '''
    A Philips amBx USB device.
    '''

    def __init__(self, deviceID, deviceNum=0, **kwargs):
        super(AMBX, self).__init__(deviceID, **kwargs)
        # find our device
        devs = devices_by_vendor_product(VENDOR, PRODUCT)

        devptr = devs[deviceNum]

        self.dev = devptr.open()
        self.dev.claimInterface(0)

    def initialise(self):
        self.allOff()

    def setColour(self, light, red, green, blue):
        return self.dev.interruptWrite(EP_OUT, B([PKT_HEADER, light, SET_LIGHT_COLOR, red, green, blue]), 100)

    def allOff(self):
        self.setColour(Lights.LEFT, 0, 0, 0)
        self.setColour(Lights.WWLEFT, 0, 0, 0)
        self.setColour(Lights.WWCENTER, 0, 0, 0)
        self.setColour(Lights.WWRIGHT, 0, 0, 0)
        self.setColour(Lights.RIGHT, 0, 0, 0)


def devices_by_vendor_product(vendor, product):
    '''
    Enumerate all USB devices with the right vendor
    and product ID
    '''
    devs = []
    for bus in usb.busses():
        for device in bus.devices:
            if device.idVendor == vendor and device.idProduct == product:
                devs.append(device)
    return devs


def B(x):
    return array("B", x)
