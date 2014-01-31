import unittest
from org.muscat.staldates.aldatesx.devices.ETCUnison import UnisonCommand,\
    CommandStringTooLongError


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
