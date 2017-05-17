import unittest
from avx.devices.serial.ETCUnison import UnisonCommand,\
    CommandStringTooLongError, UnisonDevice
from avx.devices.serial.tests.MockSerialPort import MockSerialPort


def ordify(string):
    return map(lambda a: ord(a), string)


class TestETCUnison(unittest.TestCase):

    def testUnisonCommand(self):
        cmd = UnisonCommand("Ballroom.Dinner.ACTI")

        self.assertEqual('ee1700004042616c6c726f6f6d2e44696e6e65722e414354490000', cmd.getByteString().encode('hex_codec'))

        try:
            _ = UnisonCommand("Very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very very long string")
            self.fail("Should have balked at overly lengthy command string")
        except (CommandStringTooLongError):
            pass

    def testUnisonDevice(self):
        port = MockSerialPort()
        unison = UnisonDevice("Test", port)

        def testFor(method, data, expected):
            actual = method(*data)
            self.assertBytesEqual(
                [0xEE, len(expected) + 3, 0, 0, 0x40] + ordify(expected) + [0, 0],
                port.bytes
            )
            self.assertEquals(len(expected) + 7, actual)
            port.clear()

        testFor(unison.activate, ["Test.Test.Preset1"], "Test.Test.Preset1.ACTI")
        testFor(unison.deactivate, ["Test.Test.Preset2"], "Test.Test.Preset2.DACT")
        testFor(unison.activateWithFade, ["Test.Test.Preset3", 1234], "Test.Test.Preset3.nDFT=1234")

        testFor(unison.open, ["Room1.Wall1"], "Room1.Wall1.OPEN")
        testFor(unison.close, ["Room1.Wall2"], "Room1.Wall2.CLOS")
        testFor(unison.toggleOpen, ["Room1.Wall3"], "Room1.Wall3.TOGL")

        testFor(unison.setZoneIntensity, ["Room1.Pillar Uplights", 55], "Room1.Pillar Uplights.nINT=36044")

        testFor(unison.execute, ["Disco Mode"], "Disco Mode.EXEC")
        testFor(unison.stop, ["Disco Mode"], "Disco Mode.STOP")

        testFor(unison.master, ["Room.Section Zero", 100], "Room.Section Zero.Master.nVAL=65535")

    def assertBytesEqual(self, expected, actual):
        self.assertEqual(len(expected), len(actual), "Not equal length: {} !+ {}".format(map(lambda a: chr(a), expected), actual))
        for i in range(len(expected)):
            self.assertEqual(chr(expected[i]), actual[i], "Byte " + str(i) + ", expected " + str(expected[i]) + " but received " + str(ord(actual[i])))
