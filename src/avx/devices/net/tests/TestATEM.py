from avx.devices.net.atem import ATEM, byteArrayToString, SIZE_OF_HEADER
from mock import MagicMock

import struct
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


class TestATEM(unittest.TestCase):

    def setUp(self):
        self.atem = ATEM("testAtem", "localhost", 1234)

        self.atem._socket = MagicMock()

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

    def testRecvInit(self):
        self.assertFalse(self.atem._isInitialized)

        uid = 0xAB
        self.atem._handlePacket(byteArrayToString([0x08, 0x0c, uid, 0x09, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x12]))

        self.assertTrue(self.atem._isInitialized)
        self.atem._socket.sendto.assert_called_with('\x80\x0c' + chr(uid) + '\x09\x00\x12\x00\x00\x00\x00\x00\x00', ('localhost', 1234))

########
# System setup / topology related packets
########

    def testRecv_ver(self):
        self.send_command('_ver', [0x00, 0x0B, 0x00, 0x26])
        self.assertEqual("11.38", self.atem._system_config['version'])

    def testRecv_pin(self):
        self.send_command('_pin', map(ord, 'I am not an ATEM'))
        self.assertEqual('I am not an ATEM', self.atem._system_config['name'])

    def testRecv_top(self):
        self.send_command('_top', [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])

        top = self.atem._system_config['topology']
        self.assertEqual(1, top['mes'])
        self.assertEqual(2, top['sources'])
        self.assertEqual(3, top['color_generators'])
        self.assertEqual(4, top['aux_busses'])
        self.assertEqual(5, top['dsks'])
        self.assertEqual(6, top['stingers'])
        self.assertEqual(7, top['dves'])
        self.assertEqual(8, top['supersources'])
        # Remainder of bytes are unknowns

    def testRecv_MeC(self):
        self.send_command('_MeC', [8, 27, 0])
        self.assertEqual(27, self.atem._system_config['keyers'][8])

    def testRecv_mpl(self):
        self.send_command('_mpl', [29, 42, 0])
        self.assertEqual(29, self.atem._system_config['media_players']['still'])
        self.assertEqual(42, self.atem._system_config['media_players']['clip'])

    def testRecv_MvC(self):
        self.send_command('_MvC', [17, 0])
        self.assertEqual(17, self.atem._system_config['multiviewers'])

    def testRecv_SSC(self):
        self.send_command('_SSC', [99, 0, 0, 0])
        self.assertEqual(99, self.atem._system_config['super_source_boxes'])

    def testRecv_TlC(self):
        self.send_command('_TlC', [0, 0, 0, 0, 99, 0, 0, 0])
        self.assertEqual(99, self.atem._system_config['tally_channels'])
