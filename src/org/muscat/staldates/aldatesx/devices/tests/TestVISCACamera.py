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
        
        port.setDataForRead([0x10, 0x50, 0x01, 0x02, 0x03, 0x04, 0x0A, 0x0B, 0x0C, 0x0D, 0xFF])
        
        pos = cam.getPosition()
        
        self.assertEqual(pos.pan, 0x1234)
        self.assertEqual(pos.tilt, 0xABCD)
        self.assertEqual(pos.zoom, 0x1234) # This is a bit of a hack since getPosition() results in two calls to port.read()
        

if __name__ == "__main__":
    unittest.main()