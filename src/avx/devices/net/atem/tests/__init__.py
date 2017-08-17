from avx.devices.net.atem import ATEM, SIZE_OF_HEADER, byteArrayToString
from mock import MagicMock

import struct
import time
import unittest


def _createCommandHeader(payloadSize, uid, ackId):
    buf = b''
    packageId = 0

    val = (payloadSize + SIZE_OF_HEADER)
    buf += struct.pack('!H', val)
    buf += struct.pack('!H', uid)
    buf += struct.pack('!H', ackId)
    buf += struct.pack('!I', 0)
    buf += struct.pack('!H', packageId)
    return buf


class BaseATEMTest(unittest.TestCase):
    def setUp(self):
        self.atem = ATEM("testAtem", "localhost", 1234)

        self.atem._socket = MagicMock()
        self.atem.broadcast = MagicMock()

        # We initialise the state of the ATEM but not its networking
        self.atem._initialiseState()

    def send_command(self, cmd, payload):
        size = len(cmd) + len(payload) + 4
        dg = _createCommandHeader(size, 1138, 0)
        dg += struct.pack('!H', size)
        dg += "\x00\x00"
        dg += cmd
        dg += byteArrayToString(payload)

        self.atem._handlePacket(dg)
        time.sleep(0.1)
