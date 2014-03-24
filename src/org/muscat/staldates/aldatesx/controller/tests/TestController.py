from unittest import TestCase
from org.muscat.staldates.aldatesx.controller.Controller import Controller, DuplicateDeviceIDError
from mock import MagicMock
from org.muscat.staldates.aldatesx.devices.SerialRelayCard import UpDownStopArray
import os
from org.muscat.staldates.aldatesx.devices.KramerVP88 import KramerVP88, KramerVP88Listener
from org.muscat.staldates.aldatesx.devices.SerialDevice import FakeSerialPort


class TestController(TestCase):

    def testSendControlSignalsToBlinds(self):
        c = Controller()

        blinds = UpDownStopArray("Blinds", c)
        blinds.lower = MagicMock(return_value=0)
        blinds.raiseUp = MagicMock(return_value=0)
        blinds.stop = MagicMock(return_value=0)

        c.addDevice(blinds)

        c.lower("Blinds", 1)
        blinds.lower.assert_called_once_with(1)

        c.raiseUp("Blinds", 256)
        blinds.raiseUp.assert_called_once_with(256)

        c.stop("Blinds", 1138)
        blinds.stop.assert_called_once_with(1138)

    def testLoadConfig(self):
        c = Controller()
        c.loadConfig(os.path.join(os.path.dirname(__file__), 'testConfig.json'))

        self.assertTrue(c.hasDevice("Main"))
        self.assertTrue(c.hasDevice("Main Listener"))

        self.assertTrue(isinstance(c.getDevice("Main"), KramerVP88))
        self.assertTrue(isinstance(c.getDevice("Main Listener"), KramerVP88Listener))

        self.assertEqual("testController", c.controllerID)

    def testLoadConfigWithDuplicate(self):
        c = Controller()
        try:
            c.loadConfig(os.path.join(os.path.dirname(__file__), 'testDuplicateDevice.json'))
            self.fail("Didn't throw an exception when adding a duplicated device ID")
        except DuplicateDeviceIDError as e:
            self.assertEqual("Device already exists: Duplicate", str(e))

    def testCallRemoteController(self):
        master = Controller()
        slave = Controller()

        switcher = KramerVP88("Test", FakeSerialPort())
        switcher.sendInputToOutput = MagicMock(return_value=1)

        slave.addDevice(switcher)

        self.assertFalse(master.hasDevice("Test"))
        self.assertTrue(slave.hasDevice("Test"))

        master.slaves.append(slave)

        master.switch("Test", 1, 2)
        switcher.sendInputToOutput.assert_called_once_with(1, 2)
