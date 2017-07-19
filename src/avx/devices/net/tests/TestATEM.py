from avx.devices.net.atem import ATEM, byteArrayToString, DownconverterMode, ExternalPortType, MultiviewerLayout, \
    PortType, SIZE_OF_HEADER, VideoMode, VideoSource, ClipType, MessageTypes, TransitionStyle, \
    NotInitializedException
from mock import MagicMock

import struct
import unittest
from avx.devices.Device import InvalidArgumentException


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


def zeroes(count):
    return [0 for _ in range(count)]


def bytes_of(val):
    return [(val >> 8), (val & 0xFF)]


class TestATEM(unittest.TestCase):

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

########
# Mixer state packets
########

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

    def testRecvKeOn(self):
        self.send_command('KeOn', [0, 1, 1, 0])
        self.assertEqual(True, self.atem._state['keyers'][0][1])

    def testRecvDskB(self):
        self.send_command('DskB', [0, 0, 0, 1, 0, 2, 0])
        expected = {
            'fill': VideoSource.INPUT_1,
            'key': VideoSource.INPUT_2
        }
        self.assertEqual(expected, self.atem._state['dskeyers'][0])

    def testRecvDskS(self):
        self.send_command('DskS', [0, 0, 1, 1, 17, 0, 0, 0])
        expected = {
            'on_air': False,
            'in_transition': True,
            'auto_transitioning': True,
            'frames_remaining': 17
        }
        self.assertEqual(expected, self.atem._state['dskeyers'][0])

    def testRecvAuxS(self):
        self.send_command('AuxS', [1, 0, 0x27, 0x1A])
        self.assertEqual(VideoSource.ME_1_PROGRAM, self.atem._state['aux'][1])
        self.atem.broadcast.assert_called_once_with(MessageTypes.AUX_OUTPUT_MAPPING, {1: VideoSource.ME_1_PROGRAM})

########
# Media players
########

    def testRecvRCPS(self):
        self.send_command('RCPS', [0, 1, 1, 0, 0, 24])

        expected = {
            'playing': True,
            'loop': True,
            'beginning': False,
            'clip_frame': 24
        }

        self.assertEqual(expected, self.atem._state['mediaplayer'][0])

    def testRecvMPCE(self):
        self.send_command('MPCE', [0, 1, 2, 3])

        expected = {
            'type': ClipType.STILL,
            'still_index': 2,
            'clip_index': 3
        }

        self.assertEqual(expected, self.atem._state['mediaplayer'][0])

    def testRecvMPSp(self):
        self.send_command('MPSp', [0x01, 0x1D, 0x00, 0x4B])
        expected = {
            0: {
                'maxlength': 285
            },
            1: {
                'maxlength': 75
            }
        }
        self.assertEqual(expected, self.atem._config['mediapool'])

    def testRecvMPCS(self):
        self.send_command(
            'MPCS',
            [1, 1] +
            map(ord, 'Clip Name String') +
            zeroes(48) +
            [0, 0xFF]
        )

        expected = {
            'clips': {
                1: {
                    'used': True,
                    'filename': 'Clip Name String',
                    'length': 255
                }
            }
        }

        self.assertEqual(expected, self.atem._state['mediapool'])

    def testRecvMPAS(self):
        self.send_command(
            'MPAS',
            [1, 1] +
            zeroes(16) +
            map(ord, 'Clip Name String') +
            zeroes(49)
        )

        expected = {
            'audio': {
                1: {
                    'used': True,
                    'filename': 'Clip Name String',
                }
            }
        }

        self.assertEqual(expected, self.atem._state['mediapool'])

    def testRecvMPfe(self):
        filename = 'Clip Filename String'
        self.send_command(
            'MPfe',
            [0, 0, 0, 24, 1] +
            map(ord, 'ABCDEF1234567890') +
            [0, 0, len(filename)] +
            map(ord, filename)
        )

        expected = {
            'stills': {
                24: {
                    'used': True,
                    'hash': 'ABCDEF1234567890',
                    'filename': filename,
                }
            }
        }

        self.assertEqual(expected, self.atem._state['mediapool'])

########
# Transitions
########

    def testRecvTrSS(self):
        self.send_command('TrSS', [0, 2, 3, 4, 5])
        expected = {
            0: {
                'current': {
                    'style': TransitionStyle.WIPE,
                    'tied': {
                        0: True,
                        1: True,
                        2: False,
                        3: False,
                        4: False
                    }
                },
                'next': {
                    'style': TransitionStyle.STING,
                    'tied': {
                        0: True,
                        1: False,
                        2: True,
                        3: False,
                        4: False
                    }
                }
            }
        }
        self.assertEqual(expected, self.atem._state['transition'])

    def testRecvTrPs(self):
        self.send_command('TrPs', [0, 1, 24, 0, 0x15, 0x38, 0])
        self.send_command('TrPs', [1, 0, 42, 0, 0x04, 0x72, 0])
        expected = {
            0: {
                'current': {
                    'position': 5432,
                    'frames_remaining': 24,
                    'in_transition': True
                }
            },
            1: {
                'current': {
                    'position': 1138,
                    'frames_remaining': 42,
                    'in_transition': False
                }
            }
        }
        self.assertEqual(expected, self.atem._state['transition'])

########
# Tally
########

    def testRecvTlIn(self):
        self.send_command('TlIn', [0, 4, 3, 2, 1, 0])
        expected = {
            '1': {'prv': True, 'pgm': True},
            '2': {'prv': True, 'pgm': False},
            '3': {'prv': False, 'pgm': True},
            '4': {'prv': False, 'pgm': False},
        }
        self.assertEqual(expected, self.atem._state['tally_by_index'])

    def testRecvTlSr(self):
        self.send_command('TlSr', [0, 2, 0x0B, 0xC2, 2, 0, 1, 0])

        expected = {
            VideoSource.MEDIA_PLAYER_1: {'prv': True, 'pgm': False},
            VideoSource.INPUT_1: {'prv': False, 'pgm': False}
        }
        self.assertEqual(expected.keys(), self.atem._state['tally'].keys())
        for k in expected.keys():
            self.assertEqual(expected[k], self.atem._state['tally'][k])
        self.atem.broadcast.assert_called_once_with('avx.devices.net.atem.Tally', expected)

########
# Commands what do stuff
########

    def assert_sent_packet(self, cmd, payload):
        self.assertFalse(self.atem._socket.sendto.call_args is None, '_socket.sendto never called!')
        args = self.atem._socket.sendto.call_args[0]
        self.assertEqual(2, len(args))
        packet = args[0]

        if not isinstance(payload, str):
            payload = byteArrayToString(payload)

        self.assertEqual(cmd, packet[SIZE_OF_HEADER + 4:SIZE_OF_HEADER + 8])
        self.assertEqual(payload, packet[SIZE_OF_HEADER + 8:])

    def _init_with_defaults(self):
        self.atem._handlePacket(byteArrayToString([0x08, 0x0c, 0xab, 0x09, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x12]))
        self.send_command('_top', [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
        self.send_command(
            'InPr',
            bytes_of(VideoSource.COLOUR_BARS.value) +
            map(ord, 'Input Long Name') + [0, 0, 0, 0, 0] +  # Long name always 20 bytes
            map(ord, 'InLN') +  # Short name always 4 bytes
            [0, 0x0F, 0, 1, 2, 0, 0x1E, 0x02, 0, 0]
        )
        self.atem._socket.reset_mock()

    def testSetAuxSource(self):
        try:
            self.atem.setAuxSource("Not initialised so going to fail", 0)
            self.fail("Should have thrown an exception as not initialised")
        except NotInitializedException:
            pass

        self._init_with_defaults()

        try:
            self.atem.setAuxSource(2, 0)
            self.fail("Aux 2 shouldn't exist!")
        except InvalidArgumentException:
            pass

        self.atem.setAuxSource(1, VideoSource.COLOUR_BARS)
        self.assert_sent_packet('CAuS', [1, 0] + bytes_of(VideoSource.COLOUR_BARS.value))

    def testSetPreview(self):
        try:
            self.atem.setPreview("Not initialised so going to fail", 0)
            self.fail("Should have thrown an exception as not initialised")
        except NotInitializedException:
            pass

        self._init_with_defaults()

        try:
            self.atem.setPreview(VideoSource.COLOUR_BARS, 2)
            self.fail("ME 2 shouldn't exist!")
        except InvalidArgumentException:
            pass

        self.atem.setPreview(VideoSource.COLOUR_BARS, 1)
        self.assert_sent_packet('CPvI', [0, 0] + bytes_of(VideoSource.COLOUR_BARS.value))

# OK, I think we've tested the @requiresInit and @assertTopology decorators enough now...

    def testSetProgram(self):
        self._init_with_defaults()

        self.atem.setProgram(VideoSource.COLOUR_BARS)
        self.assert_sent_packet('CPgI', [0, 0] + bytes_of(VideoSource.COLOUR_BARS.value))

    def testPerformCut(self):
        self._init_with_defaults()

        self.atem.performCut(1)
        self.assert_sent_packet('DCut', [0, 0, 0, 0])

    def testPerformAutoTake(self):
        self._init_with_defaults()
        self.atem.performAutoTake()
        self.assert_sent_packet('DAut', [0, 0, 0, 0])

    def testSetNextTransition(self):
        self._init_with_defaults()
        self.atem.setNextTransition(TransitionStyle.MIX, bkgd=True, key1=True, key2=False, key3=False, key4=False, me=1)
        self.assert_sent_packet('CTTp', [0x03, 0, 0, 0x03])

        self.atem._socket.reset_mock()
        self.atem.setNextTransition(TransitionStyle.WIPE)
        self.assert_sent_packet('CTTp', [0x01, 0, 2, 0x00])

        self.atem._socket.reset_mock()
        self.atem.setNextTransition(TransitionStyle.DIP, True, True, True, True, True)
        self.assert_sent_packet('CTTp', [0x03, 0, 1, 0x1F])
