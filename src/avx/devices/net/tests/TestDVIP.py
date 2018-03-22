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

    def testVISCACommands(self):

        def run(command, expected):
            expected_bytes = SerialDevice.byteArrayToString(expected)
            command()
            self.dvip.socket.send.assert_called_once_with(expected_bytes)
            self.dvip.socket.reset_mock()

        run(self.dvip.moveUp, [0x00, 0x0B, 0x81, 0x01, 0x06, 0x01, 0x06, 0x06, 0x03, 0x01, 0xFF])
        run(self.dvip.stop, [0x00, 0x0B, 0x81, 0x01, 0x06, 0x01, 0x06, 0x06, 0x03, 0x03, 0xFF])
        run(self.dvip.zoomOut, [0x00, 0x08, 0x81, 0x01, 0x04, 0x07, 0x36, 0xFF])
        run(lambda: self.dvip.storePreset(3), [0x00, 0x09, 0x81, 0x01, 0x04, 0x3F, 0x01, 0x03, 0xFF])
