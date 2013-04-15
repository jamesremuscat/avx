'''
Created on 18 Mar 2013

@author: jrem
'''
import unittest
from org.muscat.staldates.aldatesx.devices.tests.MockSerialPort import MockSerialPort
from org.muscat.staldates.aldatesx.devices.VISCACamera import VISCACamera


class TestVISCACamera(unittest.TestCase):

    def testGetPosition(self):
        port = MockSerialPort()

        cam = VISCACamera("Test Camera", port, 1)

        port.setDataForRead([chr(0x10), chr(0x50), chr(0x01), chr(0x02), chr(0x03), chr(0x04), chr(0x0A), chr(0x0B), chr(0x0C), chr(0x0D), chr(0xFF)])

        pos = cam.getPosition()

        self.assertEqual(pos.pan, 0x1234)
        self.assertEqual(pos.tilt, 0xABCD)
        self.assertEqual(pos.zoom, 0x1234)  # This is a bit of a hack since getPosition() results in two calls to port.read()


if __name__ == "__main__":
    unittest.main()
