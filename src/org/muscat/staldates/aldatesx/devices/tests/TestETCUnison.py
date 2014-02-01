import unittest
from org.muscat.staldates.aldatesx.devices.ETCUnison import UnisonCommand,\
    CommandStringTooLongError, UnisonDevice
from org.muscat.staldates.aldatesx.devices.tests.MockSerialPort import MockSerialPort


class TestETCUnison(unittest.TestCase):

    def testUnisonCommand(self):
        cmd = UnisonCommand("Ballroom.Dinner.ACTI")

        self.assertEqual('ee1700004042616c6c726f6f6d2e44696e6e65722e414354490000', cmd.getByteString().encode('hex_codec'))

        try:
            cmd2 = UnisonCommand("Very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very long string")
            cmd2.__class__  # never executed, only here to prevent unused variable warning
            self.fail("Should have balked at overly lengthy command string")
        except (CommandStringTooLongError):
            pass

    def testUnisonDevice(self):
        port = MockSerialPort()
        unison = UnisonDevice("Test", port)

        activate = unison.activate("Test.Test.Preset1")
        self.assertBytesEqual([0xEE, 25, 0, 0, 0x40,
                               ord('T'), ord('e'), ord('s'), ord('t'), ord('.'),
                               ord('T'), ord('e'), ord('s'), ord('t'), ord('.'),
                               ord('P'), ord('r'), ord('e'), ord('s'), ord('e'), ord('t'), ord('1'), ord('.'),
                               ord('A'), ord('C'), ord('T'), ord('I'),
                               0, 0], port.bytes)
        self.assertEquals(29, activate)

        port.clear()

        deact = unison.deactivate("Test.Test.Preset2")
        self.assertBytesEqual([0xEE, 25, 0, 0, 0x40,
                               ord('T'), ord('e'), ord('s'), ord('t'), ord('.'),
                               ord('T'), ord('e'), ord('s'), ord('t'), ord('.'),
                               ord('P'), ord('r'), ord('e'), ord('s'), ord('e'), ord('t'), ord('2'), ord('.'),
                               ord('D'), ord('A'), ord('C'), ord('T'),
                               0, 0], port.bytes)
        self.assertEquals(29, deact)

    def assertBytesEqual(self, expected, actual):
        self.assertEqual(len(expected), len(actual))
        for i in range(len(expected)):
            self.assertEqual(chr(expected[i]), actual[i], "Byte " + str(i) + ", expected " + str(expected[i]) + " but received " + str(ord(actual[i])))
