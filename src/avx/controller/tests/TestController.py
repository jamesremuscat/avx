from avx.controller.Controller import Controller, DuplicateDeviceIDError, ControllerProxy, versionsCompatible
from avx.devices.KramerVP88 import KramerVP88, KramerVP88Listener
from avx.devices.SerialDevice import FakeSerialPort
from avx.devices.SerialRelayCard import UpDownStopArray
from mock import MagicMock, call, patch
from threading import Thread
from unittest import TestCase
import os
from Pyro4.errors import NamingError


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

    @patch("avx.controller.Controller.logging")
    @patch("avx.controller.Controller.Controller.fromPyro")
    def testLoadConfigWithRemote(self, fromPyro, logging):

        c = Controller()
        fakeSlave = MagicMock()
        fakeSlave.getVersion = MagicMock(return_value=c.getVersion())
        fakeSlave.hasDevice = MagicMock(return_value=True)

        incompatibleSlave = MagicMock()
        incompatibleSlave.getVersion = MagicMock(return_value="0.1.0")

        fromPyro.side_effect = [fakeSlave, incompatibleSlave, NamingError()]

        c.loadConfig(os.path.join(os.path.dirname(__file__), 'testConfigWithSlaves.json'))

        fromPyro.assert_has_calls([
            call('slave1'),  # Boba Fett? Boba Fett? Where?
            call('incompatible'),
            call('nonexistent')
        ])

        logging.error.assert_has_calls([
            call("This Controller is version {} but tried to add slave incompatible of version 0.1.0".format(c.getVersion())),
            call("Could not connect to slave with controller ID nonexistent")
        ])
        self.assertEqual(1, len(c.slaves))

        c.proxyDevice("fakeDevice")
        fakeSlave.proxyDevice.assert_called_once_with("fakeDevice")

    @patch("avx.controller.Controller.logging")
    def testLoadConfigWithLogging(self, logging):
        mockLogger = MagicMock()
        logging.getLogger = MagicMock(return_value=mockLogger)

        c = Controller()
        c.loadConfig(os.path.join(os.path.dirname(__file__), 'testConfigWithLogging.json'), True)

        logging.config.dictConfig.assert_called_once_with({"key": "value", "key2": "value2"})
        mockLogger.setLevel.assert_called_once_with(logging.DEBUG)
        logging.info.assert_called_once_with("-d specified, overriding any specified default logger level to DEBUG")

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

    @patch("avx.controller.Controller.atexit")
    def testInitAndDeinitDevices(self, atexit):
        c = Controller()
        d = MagicMock()
        d.deviceID = "Test"
        c.addDevice(d)

        c.initialise()
        d.initialise.assert_called_once_with()
        atexit.register.assert_called_once_with(c.deinitialise)

        c.deinitialise()
        d.deinitialise.assert_called_once_with()

    def testBadClientDisconnect(self):
        c = Controller()

        c.registerClient("DOES_NOT_EXIST")
        self.assertEqual(["DOES_NOT_EXIST"], c.clients)

        c.callAllClients(lambda c: c.doesNotExist())
        self.assertEqual([], c.clients)

    def testVersionCompatibility(self):
        table = [
            # remote, local, expected
            ("0.95", "0.95", True),
            ("0.95.1", "0.95", True),
            ("0.95", "0.96", False),
            ("0.96", "0.95", False),
            ("1.0", "1.0", True),
            ("1.1", "1.0", True),
            ("1.1", "1.0.1", True),
            ("1.1.5", "1.0.1", True),
            ("1.0", "1.1", False),
            ("2.0", "1.0", False)
        ]

        for remote, local, compatible in table:
            self.assertEqual(compatible, versionsCompatible(remote, local), "Remote v{remote} unexpectedly {maybe}compatible with local v{local}".format(remote=remote, local=local, maybe="not " if compatible else ""))
