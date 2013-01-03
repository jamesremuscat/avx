'''
Created on 3 Jan 2013

@author: james
'''
import unittest
from org.muscat.staldates.aldatesx.devices.Inline3808 import Inline3808
from org.muscat.staldates.aldatesx.devices.tests.MockSerialPort import MockSerialPort
from org.muscat.staldates.aldatesx.devices.KramerVP88 import KramerVP88


class TestDevices(unittest.TestCase):


    def testInline3808(self):
        
        port = MockSerialPort()
        
        inline = Inline3808("Test", port)
        
        inline.initialise()
        
        self.assertEqual(list("[CNF290000]"), port.bytes)
        
        port.clear()
        
        inline.sendInputToOutput(3, 2)
        self.assertEqual(list("[PT1O02I03]"), port.bytes)


    def testKramerVP88(self):
        port = MockSerialPort()
        vp88 = KramerVP88("Test", port)
        
        vp88.initialise()
        self.assertEqual([], port.bytes)
        
        vp88.sendInputToOutput(2, 8)
        self.assertBytesEqual([0x01, 0x82, 0x88, 0x81], port.bytes)
        
    def assertBytesEqual(self, expected, actual):
        for i in range(len(expected)):
            self.assertEqual(chr(expected[i]), actual[i], "Byte " + str(i) + ", expected " + str(expected[i]) + " but received " + str(ord(actual[i])))
        


if __name__ == "__main__":
    unittest.main()