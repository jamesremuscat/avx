'''
Created on 21 Mar 2018

@author: james
'''
from avx.devices.net.dvip import DVIPCamera
from avx.devices.serial.SerialDevice import SerialDevice
from mock import MagicMock

import unittest


class TestDVIPCamera(unittest.TestCase):
    def setUp(self):
        self.dvip = DVIPCamera("test", "127.0.0.1")
        self.dvip.socket = MagicMock()

    def testPacketHeaders(self):
        data = [0, 0, 0, 0, 0]

        EXTRA_BYTES = 4  # Two bytes for DVIP header; one for VISCA header, one for VISCA footer
        expected = SerialDevice.byteArrayToString([0, len(data) + EXTRA_BYTES, 0x81, 0, 0, 0, 0, 0, 0xFF])
        self.dvip.sendVISCA(data)
        self.dvip.socket.send.assert_called_once_with(expected)
