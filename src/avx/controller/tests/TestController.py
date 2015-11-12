from avx.controller.Controller import Controller, DuplicateDeviceIDError, ControllerProxy
from avx.devices.KramerVP88 import KramerVP88, KramerVP88Listener
from avx.devices.SerialDevice import FakeSerialPort
from avx.devices.SerialRelayCard import UpDownStopArray
from mock import MagicMock
from threading import Thread
from unittest import TestCase
import os


class TestController(TestCase):

    class PyroThread(Thread):

        def __init__(self, daemon):
            Thread.__init__(self)
            self.daemon = daemon

        def run(self):
            self.daemon.requestLoop()

    def testSendControlSignalsToBlinds(self):
        c = Controller()
        cp = ControllerProxy(c)

        self.PyroThread(c.daemon).start()

        blinds = UpDownStopArray("Blinds", c)
        blinds.lower = MagicMock(return_value=0)
        blinds.raiseUp = MagicMock(return_value=0)
        blinds.stop = MagicMock(return_value=0)

        c.addDevice(blinds)

        cp["Blinds"].lower(1)
        blinds.lower.assert_called_once_with(1)

        cp["Blinds"].raiseUp(256)
        blinds.raiseUp.assert_called_once_with(256)

        cp["Blinds"].stop(1138)
        blinds.stop.assert_called_once_with(1138)
        c.daemon.shutdown()

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

        cp = ControllerProxy(master)

        self.PyroThread(master.daemon).start()
        self.PyroThread(slave.daemon).start()

        switcher = KramerVP88("Test", FakeSerialPort())
        switcher.sendInputToOutput = MagicMock(return_value=1)

        slave.addDevice(switcher)

        self.assertFalse(master.hasDevice("Test"))
        self.assertTrue(slave.hasDevice("Test"))

        master.slaves.append(slave)

        cp["Test"].sendInputToOutput(1, 2)
        switcher.sendInputToOutput.assert_called_once_with(1, 2)

        master.daemon.shutdown()
        slave.daemon.shutdown()
