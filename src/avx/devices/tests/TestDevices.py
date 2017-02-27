'''
Created on 3 Jan 2013

@author: james
'''
from avx.controller.Controller import Controller
from avx.devices.CoriogenEclipse import CoriogenEclipse
from avx.devices.Inline3808 import Inline3808
from avx.devices.KramerVP88 import KramerVP88, KramerVP88Listener
from avx.devices.Kramer602 import Kramer602, Kramer602Listener
from avx.devices.KramerVP703 import KramerVP703
from avx.devices.SerialDevice import SerialDevice
from avx.devices.SerialRelayCard import ICStationSerialRelayCard, JBSerialRelayCard, KMtronicSerialRelayCard,\
    UpDownStopRelay, UpDownStopArray
from avx.devices.tests.MockSerialPort import MockSerialPort
from mock import MagicMock, call, patch
import threading
import unittest
from serial.serialutil import SerialException
from avx.devices.Device import InvalidArgumentException
from time import sleep


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
        self.assertBytesEqual([0x05, 0x80, 0x81, 0x81,
                               0x05, 0x80, 0x82, 0x81,
                               0x05, 0x80, 0x83, 0x81,
                               0x05, 0x80, 0x84, 0x81,
                               0x05, 0x80, 0x85, 0x81,
                               0x05, 0x80, 0x86, 0x81,
                               0x05, 0x80, 0x87, 0x81,
                               0x05, 0x80, 0x88, 0x81], port.bytes)
        port.clear()

        vp88.sendInputToOutput(2, 8)
        self.assertBytesEqual([0x01, 0x82, 0x88, 0x81], port.bytes)

    @patch('avx.devices.Kramer602.logging')
    def testKramer602(self, logging):
        port = MockSerialPort()
        k602 = Kramer602("Test", port)

        k602.initialise()
        self.assertBytesEqual([0x0, 0xA1], port.bytes)
        port.clear()

        k602.sendInputToOutput(2, 1)
        self.assertBytesEqual([0x0, 0x83], port.bytes)

        port.clear()

        k602.sendInputToOutput(1, 2)
        self.assertBytesEqual([0x0, 0x82], port.bytes)

        k602.sendInputToOutput(2, 3)
        logging.error.assert_called_once_with("Output channel 3 does not exist on switcher Test")

    def testKramerVP703(self):
        port = MockSerialPort()
        vp703 = KramerVP703("Test", port)

        vp703.initialise()
        self.assertEqual(list(b"Overscan = 1\r\n"), port.bytes)
        port.clear()

        vp703.overscanOff()
        self.assertEqual(list(b"Overscan = 0\r\n"), port.bytes)
        port.clear()

        vp703.freeze()
        self.assertEqual(list(b"Image Freeze = 1\r\n"), port.bytes)
        port.clear()

        vp703.unfreeze()
        self.assertEqual(list(b"Image Freeze = 0\r\n"), port.bytes)
        port.clear()

        vp703.recalibrate()
        self.assertEqual(list(b"AutoTrack = 1\r\n"), port.bytes)

    def testCoriogenEclipse(self):
        port = MockSerialPort()
        ce = CoriogenEclipse("Test", port)

        ce.initialise()
        self.assertEqual([], port.bytes)

        ce.fadeIn()
        self.assertEqual(list(b"Fade = 1\r\n"), port.bytes)
        port.clear()

        ce.fadeIn()
        self.assertEqual(list(b"Fade = 1\r\n"), port.bytes)
        port.clear()

        ce.fadeOut()
        self.assertEqual(list(b"Fade = 0\r\n"), port.bytes)
        port.clear()

        ce.freeze()
        self.assertEqual(list(b"Freeze = On\r\n"), port.bytes)
        port.clear()

        ce.unfreeze()
        self.assertEqual(list(b"Freeze = Off\r\n"), port.bytes)
        port.clear()

        ce.overlayOn()
        self.assertEqual(list(b"Mode = 3\r\n"), port.bytes)
        port.clear()

        ce.overlayOff()
        self.assertEqual(list(b"Mode = 0\r\n"), port.bytes)
        port.clear()

        ce.overscanOn()
        self.assertEqual(list(b"Overscan = On\r\n"), port.bytes)
        port.clear()

        ce.overscanOff()
        self.assertEqual(list(b"Overscan = Off\r\n"), port.bytes)

    def testKMtronicSerialRelayCard(self):
        port = MockSerialPort()
        card = KMtronicSerialRelayCard("Test", port)

        card.initialise()
        self.assertEqual([], port.bytes)

        card.on(1)
        self.assertEqual(['\xFF', '\x01', '\x01'], port.bytes)
        port.clear()

        channel = card.createDevice("channel", 2)
        channel.on()
        self.assertEqual(['\xFF', '\x02', '\x01'], port.bytes)
        port.clear()
        channel.off()
        self.assertEqual(['\xFF', '\x02', '\x00'], port.bytes)

    def testJBSerialRelayCard(self):
        port = MockSerialPort()
        card = JBSerialRelayCard("Test", port)

        card.initialise()
        self.assertEqual([], port.bytes)
        port.clear()

        card.on(1)
        self.assertEqual(['\x32'], port.bytes)
        port.clear()

        channel = card.createDevice("channel", 2)
        channel.on()
        self.assertEqual(['\x34'], port.bytes)
        port.clear()
        channel.off()
        self.assertEqual(['\x35'], port.bytes)

    def testICStationSerialRelayCard(self):
        port = MockSerialPort()
        card = ICStationSerialRelayCard("Test", port)

        card.initialise()
        sleep(0.2)
        self.assertEqual(['\x50', '\x51', '\xff'], port.bytes)
        port.clear()

        card.initialise()
        self.assertEqual([], port.bytes)

        card.on(1)
        sleep(0.2)
        self.assertEqual(['\xfe'], port.bytes)
        port.clear()

        card.on(5)
        sleep(0.2)
        self.assertEqual(['\xee'], port.bytes)
        port.clear()

        card.on(8)
        sleep(0.2)
        self.assertEqual(['\x6e'], port.bytes)
        port.clear()

        card.off(5)
        sleep(0.2)
        self.assertEqual(['\x7e'], port.bytes)
        port.clear()

        try:
            card.on(9)
            self.fail("Didn't throw an exception when channel was out of range")
        except InvalidArgumentException:
            pass

    def testUpDownStopRelay(self):
        card = MagicMock()

        directionRelay = MagicMock()
        startStopRelay = MagicMock()

        card.createDevice.side_effect = [directionRelay, startStopRelay]

        card.deviceID = "Test"

        c = Controller()
        c.addDevice(card)

        udsr = UpDownStopRelay("TestUDSR", c, ("Test", 1), ("Test", 2))

        card.createDevice.assert_has_calls([
            call("TestUDSR_direction", 1),
            call("TestUDSR_startStop", 2)
        ])

        udsr.raiseUp()
        directionRelay.on.assert_called_once_with()
        startStopRelay.on.assert_called_once_with()

        startStopRelay.reset_mock()
        directionRelay.reset_mock()

        udsr.stop()
        startStopRelay.off.assert_called_once_with()
        self.assertEqual(0, directionRelay.call_count)

        startStopRelay.reset_mock()
        directionRelay.reset_mock()

        udsr.lower()
        directionRelay.off.assert_called_once_with()
        startStopRelay.on.assert_called_once_with()

    @patch("avx.devices.SerialRelayCard.logging")
    def testUpDownStopArray(self, mock_logging):
        udsr1 = MagicMock()
        udsr1.deviceID = "udsr1"
        udsr2 = MagicMock()
        udsr2.deviceID = "udsr2"

        c = Controller()
        c.addDevice(udsr1)
        c.addDevice(udsr2)

        udsa = UpDownStopArray("Test", c, {1: 'udsr1'})

        udsa.add(udsr2, 2)
        self.assertEqual(2, len(udsa.relays.items()))

        udsa.raiseUp(1)
        udsr1.raiseUp.assert_called_once_with()
        self.assertEqual(0, udsr2.raiseUp.call_count)

        udsa.lower(0)
        udsr1.lower.assert_called_once_with()
        udsr2.lower.assert_called_once_with()

        udsa.stop(2)
        udsr2.stop.assert_called_once_with()

        udsa.raiseUp(3)
        mock_logging.error.assert_called_once_with("Tried to raise relay channel 3 but no such device attached to Test")
        mock_logging.reset_mock()
        udsa.lower(-123)
        mock_logging.error.assert_called_once_with("Tried to lower relay channel -123 but no such device attached to Test")
        mock_logging.reset_mock()
        udsa.stop(42)
        mock_logging.error.assert_called_once_with("Tried to stop relay channel 42 but no such device attached to Test")

    def testKramerVP88Listener(self):
        port = MockSerialPort()
        port.read = MagicMock(return_value=[chr(0x41), chr(0x82), chr(0x83), chr(0x81)])  # Notification that input 2 sent to output 3

        k = KramerVP88("Test", port)

        c = Controller()
        c.addDevice(k)
        kl = KramerVP88Listener("TestListener", k.deviceID, c, machineNumber=1)

        dispatcher = NullDispatcher()
        dispatcher.updateOutputMappings = MagicMock()
        kl.registerDispatcher(dispatcher)
        kl.start()
        threading.Event().wait(0.1)
        kl.stop()

        dispatcher.updateOutputMappings.assert_called_with({'Test': {3: 2}})

    def testKramer602Listener(self):
        port = MockSerialPort()
        port.read = MagicMock(return_value=[chr(0x28), chr(0x81)])  # Notification that input 1 sent to output 1

        k = Kramer602("Test", port)

        c = Controller()
        c.addDevice(k)
        kl = Kramer602Listener("TestListener", k.deviceID, c, machineNumber=1)

        dispatcher = NullDispatcher()
        dispatcher.updateOutputMappings = MagicMock()
        kl.registerDispatcher(dispatcher)
        kl.start()
        threading.Event().wait(0.1)
        kl.stop()

        dispatcher.updateOutputMappings.assert_called_with({'Test': {1: 1}})

        port = MockSerialPort()
        port.read = MagicMock(return_value=[chr(0x28), chr(0x8A)])  # Notification that input 5 sent to output 2

        k = Kramer602("Test", port)
        c = Controller()
        c.addDevice(k)
        kl = Kramer602Listener("TestListener", k.deviceID, c, machineNumber=1)

        dispatcher = NullDispatcher()
        dispatcher.updateOutputMappings = MagicMock()
        kl.registerDispatcher(dispatcher)
        kl.start()
        threading.Event().wait(0.1)
        kl.stop()

        dispatcher.updateOutputMappings.assert_called_with({'Test': {2: 5}})

    def testSerialDevice(self):
        port = MockSerialPort()
        port.portstr = "TESTPORT"
        device = SerialDevice("Test", port)

        port.write = MagicMock(side_effect=SerialException("Test serial exception"))

        device.sendCommand("\x01")

        self.assertEqual(port.write.call_count, 2)

    def assertBytesEqual(self, expected, actual):
        self.assertEqual(len(expected), len(actual))
        for i in range(len(expected)):
            self.assertEqual(chr(expected[i]), actual[i], "Byte " + str(i) + ", expected " + str(expected[i]) + " but received " + str(ord(actual[i])))


class NullDispatcher(object):

    def updateOutputMappings(self):
        pass

if __name__ == "__main__":
    unittest.main()
