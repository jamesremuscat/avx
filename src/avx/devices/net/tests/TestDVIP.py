'''
Created on 21 Mar 2018

@author: james
'''
from avx.devices.net.dvip import DVIPCamera, _split_response
from avx.devices.serial.SerialDevice import SerialDevice
from mock import MagicMock
from threading import Timer

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

    def testOnReceive(self):
        self.dvip._ack = MagicMock()
        self.dvip._response_received = MagicMock()

        response_bytes = [0x03, 0x51, 0x06, 0x07, 0xFF]
        self.dvip.on_receive(
            SerialDevice.byteArrayToString(
                [
                    0x01, 0x02,  # Header
                    0x03, 0x41, 0x05, 0xFF  # Ack
                ] + response_bytes
            )
        )

        self.assertEqual(2, self.dvip._ack.set.call_count)
        self.dvip._response_received.set.assert_called_once()
        self.assertEqual(
            response_bytes,
            self.dvip._last_response
        )

    def testGetVISCA(self):
        response_bytes = [0x04, 0x51, 0xAB, 0xBA, 0xFF]

        def recv():
            self.dvip.on_receive(
                SerialDevice.byteArrayToString([
                    0x01, 0x02,
                    0x03, 0x41, 0x00, 0xFF
                ] + response_bytes)
            )

        Timer(0.2, recv).start()
        response = self.dvip.getVISCA([0, 1, 2, 3])
        self.dvip.socket.send.assert_called_once_with("\x00\x08\x81\x00\x01\x02\x03\xFF")
        self.assertEqual(response_bytes, response)


class TestSplitReceivedPackets(unittest.TestCase):
    def testSplitting(self):
        recvd = '\x00\x00\x01\x02\x03\x04\xFF\x05\x06\xFF\x07\x08\x09\xFF'
        split = _split_response(recvd)

        self.assertEqual(len(split), 3)

        self.assertEqual(
            split,
            [
                [1, 2, 3, 4, 0xFF],
                [5, 6, 0xFF],
                [7, 8, 9, 0xFF]
            ]
        )
