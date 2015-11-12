'''
Created on 18 Mar 2013

@author: jrem
'''
import unittest
from avx.devices.tests.MockSerialPort import MockSerialPort
from avx.devices.VISCACamera import VISCACamera, Aperture


class TestVISCACamera(unittest.TestCase):

    def testGetPosition(self):
        port = MockSerialPort()

        cam = VISCACamera("Test Camera", port, 1)

        port.setDataForRead([chr(0x10), chr(0x50), chr(0x01), chr(0x02), chr(0x03), chr(0x04), chr(0x0A), chr(0x0B), chr(0x0C), chr(0x0D), chr(0xFF)])

        pos = cam.getPosition()

        self.assertEqual(pos.pan, 0x1234)
        self.assertEqual(pos.tilt, 0xABCD)
        self.assertEqual(pos.zoom, 0x1234)  # This is a bit of a hack since getPosition() results in two calls to port.read()

    def testSetAperture(self):
        port = MockSerialPort()

        cam = VISCACamera("Test Camera", port, 1)

        cam.setAperture(Aperture.F28)
        self.assertBytesEqual([0x81, 0x01, 0x04, 0x4B, 0x00, 0x00, 0x00, 0x01, 0xFF], port.bytes)

        port.clear()
        cam.setAperture(Aperture.F1_8)
        self.assertBytesEqual([0x81, 0x01, 0x04, 0x4B, 0x00, 0x00, 0x01, 0x01, 0xFF], port.bytes)

    def assertBytesEqual(self, expected, actual):
        self.assertEqual(len(expected), len(actual))
        for i in range(len(expected)):
            self.assertEqual(chr(expected[i]), actual[i], "Byte " + str(i) + ", expected " + str(expected[i]) + " but received " + str(ord(actual[i])))


if __name__ == "__main__":
    unittest.main()
