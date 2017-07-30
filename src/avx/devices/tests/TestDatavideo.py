from avx.devices.datavideo import PTC150
from avx.devices.Device import InvalidArgumentException
from mock import MagicMock

import unittest


class TestDatavideo(unittest.TestCase):
    def testPTC150(self):
        port = MagicMock()
        camera = PTC150("Test", port, 1)

        try:
            camera.storePreset(0)
            self.fail("Preset 0 should be out of range")
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
