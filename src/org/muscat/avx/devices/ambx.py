from org.muscat.avx.devices.Device import Device
import usb
from array import array


# Usb identification
VENDOR = 0x0471
PRODUCT = 0x083f

# Endpoints
EP_IN = 0x81
EP_OUT = 0x02
EP_PNP = 0x83

# Packet start
PKT_HEADER = 0xA1

# -- Commands --

# Set a single color, for a specific light
# Params 0xRR 0xGG 0xBB
# 0xRR = Red color
# 0xGG = Green color
# 0xBB = Blue color
SET_LIGHT_COLOR = 0x03

# Set a color sequence using delays
# Params 0xMM 0xMM then a repeated sequence of 0xRR 0xGG 0xBB
# 0xMM = milliseconds
# 0xMM = milliseconds
# 0xRR = Red color
# 0xGG = Green color
# 0xBB = Blue color
SET_TIMED_COLOR_SEQUENCE = 0x72


# -- Lights --
# Definitions so we do not need to remember the hex values for the lights
class Lights:
    # LEFT/RIGHT lights. Normally placed adjecent to your screen.
    LEFT = 0x0B
    RIGHT = 0x1B

    # Wallwasher lights. Normally placed behind your screen.
    WWLEFT = 0x2B
    WWCENTER = 0x3B
    WWRIGHT = 0x4B


class AMBX(Device):
    '''
    A Philips amBx USB device.
    '''

    def __init__(self, deviceID, **kwargs):
        super(AMBX, self).__init__(deviceID)
        # find our device
        devs = self.devices_by_vendor_product(VENDOR, PRODUCT)

        devptr = devs[0]

        self.dev = devptr.open()
        self.dev.claimInterface(0)

    def initialise(self):
        self.setColour(Lights.LEFT, 0, 0, 0)
        self.setColour(Lights.WWLEFT, 0, 0, 0)
        self.setColour(Lights.WWCENTER, 0, 0, 0)
        self.setColour(Lights.WWRIGHT, 0, 0, 0)
        self.setColour(Lights.RIGHT, 0, 0, 0)

    def setColour(self, light, red, green, blue):
        return self.dev.interruptWrite(EP_OUT, B([PKT_HEADER, light, SET_LIGHT_COLOR, red, green, blue]), 100)

    @staticmethod
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
