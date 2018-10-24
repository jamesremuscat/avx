from avx.devices.datavideo import PTC150, PTC150_DVIP
from avx.devices.Device import InvalidArgumentException
from mock import MagicMock

import unittest


class TestDatavideo(unittest.TestCase):
    def testPTC150(self):
        port = MagicMock()
        camera = PTC150("Test", port, 1)

        try:
            camera.storePreset(-1)
            self.fail("Preset -1 should be out of range")
        except InvalidArgumentException:
            pass

        try:
            camera.storePreset(51)
            self.fail("Preset 51 should be out of range")
        except InvalidArgumentException:
            pass

        camera.storePreset(7)
        port.write.assert_called_once_with('\x81\x01\x04\x3f\x01\x07\xff')
        port.reset_mock()
        camera._wait_for_ack.release()

        camera.tallyGreen()
        port.write.assert_called_once_with('\x81\x01\x7E\x01\x0A\x00\x03\x02\xFF')
        port.reset_mock()
        camera._wait_for_ack.release()

        camera.tallyRed()
        port.write.assert_called_once_with('\x81\x01\x7E\x01\x0A\x00\x02\x00\xFF')
        port.reset_mock()
        camera._wait_for_ack.release()

        camera.tallyOff()
        port.write.assert_called_once_with('\x81\x01\x7E\x01\x0A\x00\x03\xFF')
        port.reset_mock()
        camera._wait_for_ack.release()

    def testPTC150_DVIP(self):
        socket = MagicMock()
        camera = PTC150_DVIP("Test", "127.0.0.1")
        camera.socket = socket

        camera.tallyGreen()
        socket.send.assert_called_once_with('\x00\x0B\x81\x01\x7E\x01\x0A\x00\x00\x02\xFF')
        socket.reset_mock()
