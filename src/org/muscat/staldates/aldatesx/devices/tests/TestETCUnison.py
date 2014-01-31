import unittest
from org.muscat.staldates.aldatesx.devices.ETCUnison import UnisonCommand


class TestETCUnison(unittest.TestCase):

    def testUnisonCommand(self):
        cmd = UnisonCommand("Ballroom.Dinner.ACTI")

        self.assertEqual('ee1700004042616c6c726f6f6d2e44696e6e65722e414354490000', cmd.getByteString().encode('hex_codec'))
