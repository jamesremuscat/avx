from avx.devices.net.atem import ATEM, byteArrayToString, DownconverterMode, ExternalPortType, MultiviewerLayout, \
    PortType, SIZE_OF_HEADER, VideoMode, VideoSource
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

    def testRecv_AMC(self):
        self.send_command('_AMC', [42, 1, 0])
        self.assertEqual(42, self.atem._system_config['audio_channels'])
        self.assertTrue(self.atem._system_config['has_monitor'])

    def testRecv_VMC(self):
        self.send_command('_VMC', [0, 0xFF, 0xFF, 0xC0])

        expected = {v: True for v in VideoMode}

        self.assertEqual(expected, self.atem._system_config['video_modes'])

    def testRecv_MAC(self):
        self.send_command('_MAC', [12, 0, 0, 0])
        self.assertEqual(12, self.atem._system_config['macro_banks'])

    def testRecvPowr(self):
        self.send_command('Powr', [0x3, 0x0, 0x0, 0x0])
        self.assertEqual({'main': True, 'backup': True}, self.atem._status['power'])

    def testRecvDcOt(self):
        self.send_command('DcOt', [2, 0, 0])
        self.assertEqual(DownconverterMode.ANAMORPHIC, self.atem._config['down_converter'])

    def testRecvVidM(self):
        self.send_command('VidM', [17])
        self.assertEqual(VideoMode.HD_4K_29, self.atem._config['video_mode'])

    def testRecvInPr(self):
        self.send_command(
            'InPr',
            [0, 2] +
            map(ord, 'Input Long Name') + [0, 0, 0, 0, 0] +  # Long name always 20 bytes
            map(ord, 'InLN') +  # Short name always 4 bytes
            [0, 0x0F, 0, 1, 2, 0, 0x1E, 0x02, 0, 0]
        )

        self.maxDiff = None

        expected = {
            2: {
                'availability': {
                    'Auxilary': True,
                    'KeySource': False,
                    'Multiviewer': True,
                    'SuperSourceArt': True,
                    'SuperSourceBox': True
                },
                'me_availability': {
                    'ME1': True,
                    'ME2': False
                },
                'name_long': u'Input Long Name',
                'name_short': u'InLN',
                'port_type_external': ExternalPortType.SDI,
                'port_type_internal': PortType.COLOR_BARS,
                'types_available': {
                    0: False,
                    1: True,
                    2: True,
                    3: True,
                    4: True
                }
            }
        }

        self.assertEqual(expected, self.atem._system_config['inputs'])

    def testRecvMvPr(self):
        self.send_command('MvPr', [0, 2, 0])
        self.assertEqual(MultiviewerLayout.LEFT, self.atem._config['multiviewers'][0]['layout'])

    def testRecvMvIn(self):
        self.send_command('MvIn', [0, 3, 0x1F, 0x46])
        self.assertEqual(VideoSource.AUX_6, self.atem._config['multiviewers'][0]['windows'][3])

    def testRecvPrgI(self):
        self.send_command('PrgI', [0, 0, 0x03, 0xE8])
        self.send_command('PrgI', [1, 0, 0, 15])
        self.assertEqual(VideoSource.COLOUR_BARS, self.atem._state['program'][0])
        self.assertEqual(VideoSource.INPUT_15, self.atem._state['program'][1])

    def testRecvPrvI(self):
        self.send_command('PrvI', [0, 0, 0x03, 0xE8])
        self.send_command('PrvI', [1, 0, 0, 15])
        self.assertEqual(VideoSource.COLOUR_BARS, self.atem._state['preview'][0])
        self.assertEqual(VideoSource.INPUT_15, self.atem._state['preview'][1])
