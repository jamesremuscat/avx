'''
Created on 3 Jan 2013

@author: james
'''
import unittest
from org.muscat.staldates.aldatesx.devices.Inline3808 import Inline3808
from org.muscat.staldates.aldatesx.devices.tests.MockSerialPort import MockSerialPort
from org.muscat.staldates.aldatesx.devices.KramerVP88 import KramerVP88, KramerVP88Listener
from org.muscat.staldates.aldatesx.devices.Kramer602 import Kramer602
from org.muscat.staldates.aldatesx.devices.KramerVP703 import KramerVP703
from org.muscat.staldates.aldatesx.devices.CoriogenEclipse import CoriogenEclipse
from org.muscat.staldates.aldatesx.devices.SerialRelayCard import SerialRelayCard
from mock import MagicMock


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

    def testKramer602(self):
        port = MockSerialPort()
        k602 = Kramer602("Test", port)

        k602.initialise()
        self.assertEqual([], port.bytes)

        k602.sendInputToOutput(2, 1)
        self.assertBytesEqual([0x0, 0x83], port.bytes)

        port.clear()

        k602.sendInputToOutput(1, 2)
        self.assertBytesEqual([0x0, 0x82], port.bytes)

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

    def testSerialRelayCard(self):
        port = MockSerialPort()
        card = SerialRelayCard("Test", port)

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

    def testKramerVP88Listener(self):
        port = MockSerialPort()
        port.read = MagicMock(return_value=[chr(0x41), chr(0x82), chr(0x83), chr(0x81)])  # Notification that input 2 sent to output 3
        kl = KramerVP88Listener(port, machineNumber=1)

        class NullDispatcher(object):

            def updateOutputMappings(self):
                pass

        dispatcher = NullDispatcher()
        dispatcher.updateOutputMappings = MagicMock()
        kl.registerDispatcher(dispatcher)

        kl.start()
        dispatcher.updateOutputMappings.assert_called_with({3: 2})
        kl.stop()

    def assertBytesEqual(self, expected, actual):
        for i in range(len(expected)):
            self.assertEqual(chr(expected[i]), actual[i], "Byte " + str(i) + ", expected " + str(expected[i]) + " but received " + str(ord(actual[i])))


if __name__ == "__main__":
    unittest.main()
